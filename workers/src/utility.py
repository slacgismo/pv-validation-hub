import json
from dask.delayed import delayed
from dask.distributed import Client
from dask import config

from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
    thread,
)
from functools import wraps
from logging import Logger
from time import perf_counter, sleep, time
import os
from typing import Any, Callable, Tuple, TypeVar, Union
import logging
import boto3
import botocore.exceptions
from distributed import LocalCluster
from matplotlib.pylab import f
import psutil
import requests
import math


WORKER_ERROR_PREFIX = "wr"
RUNNER_ERROR_PREFIX = "op"
SUBMISSION_ERROR_PREFIX = "sb"


T = TypeVar("T")

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


def logger_if_able(
    message: str, logger: Logger | None = None, level: str = "INFO"
):
    if logger is not None:
        levels_dict = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        level = level.upper()

        if level not in levels_dict:
            raise Exception(f"Invalid log level: {level}")

        log_level = levels_dict[level]

        logger.log(log_level, message)
    else:
        print(message)


def get_error_codes_dict(
    dir: str, prefix: str, logger: Logger | None
) -> dict[str, str]:
    try:
        with open(
            os.path.join(dir, "errorcodes.json"), "r"
        ) as error_codes_file:
            error_codes = json.load(error_codes_file)
            if prefix not in error_codes:
                logger_if_able(
                    f"Error prefix {prefix} not found in error codes file",
                    logger,
                    "ERROR",
                )

                raise KeyError(
                    f"Error prefix {prefix} not found in error codes file"
                )
            return error_codes[prefix]
    except FileNotFoundError:
        logger_if_able("Error codes file not found", logger, "ERROR")
        raise FileNotFoundError("Error codes file not found")
    except KeyError:
        logger_if_able(
            f"Error prefix {prefix} not found in error codes file",
            logger,
            "ERROR",
        )
        raise KeyError(f"Error prefix {prefix} not found in error codes file")
    except Exception as e:
        logger_if_able(f"Error loading error codes: {e}", logger, "ERROR")
        raise e


submission_error_codes = get_error_codes_dict(
    FILE_DIR, SUBMISSION_ERROR_PREFIX, None
)


def timing(verbose: bool = True, logger: Union[Logger, None] = None):
    @wraps(timing)
    def decorator(func: Callable[..., T]):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[T, float]:
            start_time = perf_counter()
            result = func(*args, **kwargs)
            end_time = perf_counter()
            execution_time = end_time - start_time
            if verbose:
                msg = (
                    f"{func.__name__} took {execution_time:.3f} seconds to run"
                )
                logger_if_able(msg, logger)
            return result, execution_time

        return wrapper

    return decorator


def multiprocess(
    func: Callable[..., T], data: list, n_processes: int, logger: Logger | None
) -> list[T]:
    log = logger or print
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        futures = {executor.submit(func, d): d for d in data}
        results: list[T] = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                log.error(f"Error: {e}")
    return results


def timeout(seconds: int, logger: Union[Logger, None] = None):
    def decorator(func: Callable[..., T]):
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except TimeoutError:
                    error_code = 1
                    raise SubmissionException(
                        *get_error_by_code(
                            error_code, submission_error_codes, logger
                        )
                    )

        return wrapper

    return decorator


def set_workers_and_threads(
    cpu_count: int | None,
    sys_memory: float,
    memory_per_run: float | int,
    n_workers: int | None = None,
    threads_per_worker: int | None = None,
    logger: Logger | None = None,
) -> Tuple[int, int]:

    def handle_exceeded_resources(
        n_workers, threads_per_worker, memory_per_run, sys_memory
    ):
        if memory_per_run * n_workers * threads_per_worker > sys_memory:
            config.set({"distributed.worker.memory.spill": True})
            logger_if_able(
                f"Memory per worker exceeds system memory ({memory_per_run} GB), activating memory spill",
                logger,
                "WARNING",
            )

    total_workers: int = 1
    total_threads: int = 1

    if cpu_count is None:
        raise Exception(10, "Could not determine number of CPUs.")

    if n_workers is not None and threads_per_worker is not None:
        if n_workers * threads_per_worker > cpu_count:
            raise Exception(
                9,
                f"workers and threads exceed local resources, {cpu_count} cores present",
            )
        handle_exceeded_resources(
            n_workers, threads_per_worker, memory_per_run, sys_memory
        )
        total_workers, total_threads = n_workers, threads_per_worker

    if n_workers is not None and threads_per_worker is None:
        threads_per_worker = int(
            math.floor(sys_memory / (memory_per_run * n_workers))
        )
        if threads_per_worker == 0:
            logger_if_able(
                "Not enough memory for a worker, defaulting to 1 thread per worker",
                logger,
                "WARNING",
            )
            threads_per_worker = 1
        handle_exceeded_resources(
            n_workers, threads_per_worker, memory_per_run, sys_memory
        )

        total_workers, total_threads = n_workers, threads_per_worker

    if n_workers is None and threads_per_worker is not None:
        n_workers = int(
            math.floor(sys_memory / (memory_per_run * threads_per_worker))
        )
        if n_workers == 0:
            logger_if_able(
                "Not enough memory for a worker, defaulting to 1 worker",
                logger,
                "WARNING",
            )
            n_workers = 1
        handle_exceeded_resources(
            n_workers, threads_per_worker, memory_per_run, sys_memory
        )

        total_workers, total_threads = n_workers, threads_per_worker

    if n_workers is None and threads_per_worker is None:

        thread_worker_total = math.floor(sys_memory / memory_per_run)
        if thread_worker_total < 1:
            logger_if_able(
                "Not enough memory for a worker, defaulting to 1 worker and 1 thread per worker",
                logger,
                "WARNING",
            )
            n_workers = 1
            threads_per_worker = 1
            handle_exceeded_resources(
                n_workers, threads_per_worker, memory_per_run, sys_memory
            )

            total_workers, total_threads = n_workers, threads_per_worker
            return total_workers, total_threads
        else:
            logger_if_able(
                f"thread_worker_total: {thread_worker_total}",
                logger,
                "DEBUG",
            )
            n_workers = int(math.ceil(thread_worker_total / 2))
            threads_per_worker = int(math.floor(thread_worker_total / 2))
            if n_workers + threads_per_worker != thread_worker_total:
                logger_if_able(
                    f"n_workers: {n_workers}, threads_per_worker: {threads_per_worker}, thread_worker_total: {thread_worker_total}",
                    logger,
                    "INFO",
                )
                logger_if_able(
                    "Could not determine number of workers and threads",
                    logger,
                    "ERROR",
                )
                raise Exception(
                    9, "Could not determine number of workers and threads"
                )
            handle_exceeded_resources(
                n_workers, threads_per_worker, memory_per_run, sys_memory
            )

            total_workers, total_threads = n_workers, threads_per_worker

    while total_workers * total_threads > cpu_count:
        if total_workers > 1:
            total_workers -= 1
        elif total_threads > 1:
            total_threads -= 1
        else:
            raise Exception(
                9, "Could not determine number of workers and threads"
            )

    return total_workers, total_threads


def dask_multiprocess(
    func: Callable[..., T],
    func_arguments: list[tuple[Any, ...]],
    n_workers: int | None = None,
    threads_per_worker: int | None = None,
    memory_per_run: float | int | None = None,
    logger: Logger | None = None,
    **kwargs,
) -> list[T]:

    MEMORY_PER_RUN = 7.0  # in GB

    memory_per_run = memory_per_run or MEMORY_PER_RUN

    cpu_count = os.cpu_count()

    sys_memory = psutil.virtual_memory().total / (1024.0**3)  # in GB

    # config.set({"distributed.worker.memory.spill": True})
    config.set({"distributed.worker.memory.pause": True})
    config.set({"distributed.worker.memory.target": 0.95})
    config.set({"distributed.worker.memory.terminate": False})

    total_workers, total_threads = set_workers_and_threads(
        cpu_count,
        sys_memory,
        memory_per_run,
        n_workers,
        threads_per_worker,
        logger,
    )

    memory_per_worker = memory_per_run * total_threads

    logger_if_able(f"cpu count: {cpu_count}", logger, "INFO")
    logger_if_able(f"memory: {sys_memory}", logger, "INFO")
    logger_if_able(f"memory per run: {memory_per_run}", logger, "INFO")
    logger_if_able(f"n_workers: {total_workers}", logger, "INFO")
    logger_if_able(f"threads_per_worker: {total_threads}", logger, "INFO")
    logger_if_able(f"memory per worker: {memory_per_worker}", logger, "INFO")

    results: list[T] = []

    with Client(
        n_workers=total_workers,
        threads_per_worker=total_threads,
        memory_limit=f"{memory_per_worker}GiB",
        **kwargs,
    ) as client:

        logger_if_able(f"client: {client}", logger, "INFO")

        lazy_results = []
        for args in func_arguments:
            lazy_result = delayed(func, pure=True)(*args)
            lazy_results.append(lazy_result)

        futures = client.compute(lazy_results)

        results = client.gather(futures)  # type: ignore

    return results


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return "PROD" not in os.environ


class WorkerException(Exception):
    def __init__(
        self, code: int, message: str, error_rate: float | None = None
    ):
        self.code = f"{WORKER_ERROR_PREFIX}_{code}"
        self.message = message
        self.error_rate = error_rate


class RunnerException(Exception):
    def __init__(
        self, code: int, message: str, error_rate: float | None = None
    ):
        self.code = f"{RUNNER_ERROR_PREFIX}_{code}"
        self.message = message
        self.error_rate = error_rate


class SubmissionException(Exception):
    def __init__(
        self, code: int, message: str, error_rate: float | None = None
    ):
        self.code = f"{SUBMISSION_ERROR_PREFIX}_{code}"
        self.message = message
        self.error_rate = error_rate


def pull_from_s3(
    IS_LOCAL: bool,
    S3_BUCKET_NAME: str,
    s3_file_path: str,
    local_file_path: str,
    logger: Logger,
) -> str:
    logger.info(f"pull file {s3_file_path} from s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        logger.info("running locally")
        s3_file_full_path = "http://s3:5000/get_object/" + s3_file_path
        # s3_file_full_path = 'http://localhost:5000/get_object/' + s3_file_path
    else:
        logger.info("running in ecs")
        s3_file_full_path = "s3://" + s3_file_path

    target_file_path = os.path.join(
        local_file_path, s3_file_full_path.split("/")[-1]
    )

    if IS_LOCAL:
        r = requests.get(s3_file_full_path, stream=True)
        if not r.ok:
            logger.error(f"Error: {r.content}")

            raise requests.HTTPError(
                2, f"Error downloading file from s3: {r.content}"
            )
        with open(target_file_path, "wb") as f:
            f.write(r.content)
    else:
        s3 = boto3.client("s3")

        # check s3_dir string to see if it contains "pv-validation-hub-bucket/"
        # if so, remove it
        s3_file_path = s3_file_path.replace("pv-validation-hub-bucket/", "")
        logger.info(
            f"dir after removing pv-validation-hub-bucket/ returns {s3_file_path}"
        )

        try:
            logger.info(
                f"Downloading {s3_file_path} from {S3_BUCKET_NAME} to {target_file_path}"
            )
            s3.download_file(S3_BUCKET_NAME, s3_file_path, target_file_path)

        except botocore.exceptions.ClientError as e:
            logger.error(f"Error: {e}")
            raise requests.HTTPError(
                2, f"File {target_file_path} not found in s3 bucket."
            )

    return target_file_path


def get_error_by_code(
    error_code: int, error_codes_dict: dict[str, str], logger: Logger | None
) -> tuple[int, str]:
    if error_codes_dict is None:
        logger_if_able("Error codes dictionary is None", logger, "ERROR")
        raise ValueError("Error codes dictionary is None")
    error_code_str = str(error_code)
    if error_code_str not in error_codes_dict:
        logger_if_able(
            f"Error code {error_code} not found in error codes",
            logger,
            "ERROR",
        )
        raise KeyError(f"Error code {error_code} not found in error codes")
    return error_code, error_codes_dict[error_code_str]


# API Utility Functions

IS_LOCAL = is_local()

API_BASE_URL = (
    "http://api:8005" if IS_LOCAL else "http://api.pv-validation-hub.org"
)

S3_BASE_URL = "http://s3:5000/get_object/" if IS_LOCAL else "s3://"


def method_request(
    method: str,
    url: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    logger_if_able(f"{method} request to {url}", logger)

    base_headers = {
        "Content-Type": "application/json",
    }

    all_headers = {**base_headers, **headers} if headers else base_headers

    body = json.dumps(data) if data else None

    response = requests.request(method, url, headers=all_headers, data=body)

    return response


def login_to_API(username: str, password: str, logger: Logger | None = None):

    login_url = f"{API_BASE_URL}/login"

    json_body = request_handler(
        "POST", login_url, {"username": username, "password": password}
    )

    if "token" not in json_body:
        logger_if_able("Token not in response", logger, "ERROR")
        raise Exception("Token not in response")
    token: str = json_body["token"]
    return token


def with_credentials(logger: Logger | None = None):

    username = os.environ.get("admin_username")
    password = os.environ.get("admin_password")

    if not username or not password:
        raise Exception("Missing admin credentials")

    api_auth_token = None
    headers = {}

    def decorator(func: Callable[..., T]):
        # @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal api_auth_token
            if not api_auth_token:
                logger_if_able("Logging in", logger)
                api_auth_token = login_to_API(username, password, logger)
                headers["Authorization"] = f"Token {api_auth_token}"
            kwargs["auth"] = headers
            return func(*args, **kwargs)

        return wrapper

    return decorator


@with_credentials()
def request_to_API_w_credentials(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
    **kwargs: Any,
):

    url = f"{API_BASE_URL}/{endpoint}"

    auth_header: dict[str, str] | None = (
        kwargs["auth"] if "auth" in kwargs else None
    )

    if auth_header is None:
        raise Exception("No auth header found")

    if headers is None:
        headers = {}

    headers = {**headers, **auth_header}

    data = request_handler(method, url, data, headers, logger)
    return data


def request_to_API(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    url = f"{API_BASE_URL}/{endpoint}"

    data = request_handler(method, url, data, headers, logger)
    return data


def request_to_s3(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    url = f"{S3_BASE_URL}{endpoint}"

    data = request_handler(method, url, data, headers, logger)
    return data


def request_handler(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    r = method_request(method, endpoint, headers=headers, data=data)
    if not r.ok:
        logger_if_able(f"Error: {r.text}", logger, "ERROR")
        raise Exception("Failed to get data")
    json_body: dict[str, Any] = json.loads(r.text)
    return json_body


if __name__ == "__main__":

    def expensive_function(x):
        print(x)
        sleep(2)
        return x**2

    data = list(range(10))
    func_args = [(d,) for d in data]
    n_processes = 2
    threads_per_worker = 1
    logger = None
    results = dask_multiprocess(
        expensive_function,
        [(d,) for d in data],
        n_workers=n_processes,
        threads_per_worker=threads_per_worker,
        logger=logger,
    )
    print(results)
