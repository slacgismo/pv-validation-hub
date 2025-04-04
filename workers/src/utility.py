from dataclasses import dataclass
from functools import wraps
import json
import logging
import shutil
from types import TracebackType
from dask.delayed import delayed, Delayed  # type: ignore
from dask.distributed import Client
from dask import config
import docker
from docker.models.containers import Container
from docker.errors import ImageNotFound, BuildError, APIError
from docker.models.images import Image

from concurrent.futures import (
    ThreadPoolExecutor,
)
from time import perf_counter
import os
from typing import (
    Any,
    Callable,
    ParamSpec,
    Tuple,
    TypeVar,
    TypedDict,
    Union,
    cast,
)
import boto3
import botocore.exceptions
from mypy_boto3_s3 import S3Client
from mypy_boto3_secretsmanager import SecretsManagerClient
import psutil
import requests
import math
import subprocess
import pandas as pd

from logger import setup_logging


logger = setup_logging(__name__)

WORKER_ERROR_PREFIX = "wr"
RUNNER_ERROR_PREFIX = "op"
SUBMISSION_ERROR_PREFIX = "sb"

S3_BUCKET_NAME = "pv-validation-hub-bucket"

SUBMITTING = "submitting"
SUBMITTED = "submitted"
RUNNING = "running"
FAILED = "failed"
FINISHED = "finished"


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return "PROD" not in os.environ


IS_LOCAL = is_local()

API_BASE_URL = "api:8005" if IS_LOCAL else "api.pv-validation-hub.org"


T = TypeVar("T")
P = ParamSpec("P")

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass(frozen=True)
class SubmissionFunctionArgs:
    submission_id: int
    image_tag: str
    memory_limit: str
    submission_file_name: str
    submission_function_name: str
    submission_args: Tuple[Any, ...]
    volume_data_dir: str
    volume_results_dir: str
    logger: logging.Logger

    def to_tuple(self):
        return (
            self.submission_id,
            self.image_tag,
            self.memory_limit,
            self.submission_file_name,
            self.submission_function_name,
            self.submission_args,
            self.volume_data_dir,
            self.volume_results_dir,
            self.logger,
        )


def logger_if_able(
    message: object, logger: logging.Logger | None = None, level: str = "INFO"
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
    dir: str, prefix: str, logger: logging.Logger | None
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

worker_error_codes = get_error_codes_dict(FILE_DIR, WORKER_ERROR_PREFIX, None)


def timing(verbose: bool = True, logger: Union[logging.Logger, None] = None):
    # @wraps(timing)
    def decorator(func: Callable[P, T]):
        # @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Tuple[T, float]:
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


# def multiprocess(
#     func: Callable[P, T], data: list, n_processes: int, logger: Logger | None
# ) -> list[T]:
#     log = logger or print
#     with ProcessPoolExecutor(max_workers=n_processes) as executor:
#         futures = {executor.submit(func, d): d for d in data}
#         results: list[T] = []
#         for future in as_completed(futures):
#             try:
#                 results.append(future.result())
#             except Exception as e:
#                 log.error(f"Error: {e}")
#     return results


def timeout(seconds: int, logger: Union[logging.Logger, None] = None):
    def decorator(func: Callable[P, T]):
        # @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
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
    logger: logging.Logger | None = None,
) -> Tuple[int, int]:

    def handle_exceeded_resources(
        n_workers: int,
        threads_per_worker: int,
        memory_per_run: float | int,
        sys_memory: float,
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


U = TypeVar("U")


def dask_multiprocess(
    func: Callable[P, T],
    function_args_list: list[tuple[U, ...]],
    n_workers: int | None = None,
    threads_per_worker: int | None = None,
    memory_per_run: float | int | None = None,
    logger: logging.Logger | None = None,
    **kwargs: Any,
) -> list[T]:

    MEMORY_PER_RUN = 8.0  # in GB

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

        lazy_results: list[Delayed] = []
        for args in function_args_list:
            submission_fn_args = args
            logger_if_able(f"args: {submission_fn_args}", logger, "INFO")

            lazy_result = cast(
                Delayed, delayed(func, pure=True)(*submission_fn_args)
            )
            lazy_results.append(lazy_result)

        futures = client.compute(lazy_results)  # type: ignore

        results = client.gather(futures)  # type: ignore

    return results


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


def list_s3_bucket(s3_dir: str):
    logger.info(f"list s3 bucket {s3_dir}")
    if s3_dir.startswith("/"):
        s3_dir = s3_dir[1:]

    if IS_LOCAL:
        s3_dir_full_path = "http://s3:5000/list_bucket/" + s3_dir
        # s3_dir_full_path = 'http://127.0.0.1:5000/list_bucket/' + s3_dir
    else:
        s3_dir_full_path = "s3://" + s3_dir

    all_files: list[str] = []
    if IS_LOCAL:
        r = requests.get(s3_dir_full_path)
        ret = r.json()
        for entry in ret["Contents"]:
            all_files.append(os.path.join(s3_dir.split("/")[0], entry["Key"]))
    else:
        # check s3_dir string to see if it contains "pv-validation-hub-bucket/"
        # if so, remove it
        s3_dir = s3_dir.replace("pv-validation-hub-bucket/", "")
        logger.info(
            f"dir after removing pv-validation-hub-bucket/ returns {s3_dir}"
        )

        s3: S3Client = boto3.client("s3")  # type: ignore
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=s3_dir)
        for page in pages:
            if page["KeyCount"] > 0:
                if "Contents" in page:
                    for entry in page["Contents"]:
                        if "Key" in entry:
                            all_files.append(entry["Key"])

        # remove the first entry if it is the same as s3_dir
        if len(all_files) > 0 and all_files[0] == s3_dir:
            all_files.pop(0)

    logger.info(f"listed s3 bucket {s3_dir_full_path} returns {all_files}")
    return all_files


def update_submission_status(submission_id: int, new_status: str):
    # route needs to be a string stored in a variable, cannot parse in deployed environment
    api_route = f"submissions/change_submission_status/{submission_id}"

    try:
        data = request_to_API_w_credentials(
            "PUT", api_route, data={"status": new_status}
        )
        return data
    except Exception as e:
        logger.error(f"Error updating submission status to {new_status}")
        logger.exception(e)
        error_code = 5
        raise WorkerException(
            *get_error_by_code(error_code, worker_error_codes, logger),
        )


def push_to_s3(local_file_path: str, s3_file_path: str, submission_id: int):
    logger.info(f"push file {local_file_path} to s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        s3_file_full_path = (
            f"http://s3:5000/put_object/{S3_BUCKET_NAME}/" + s3_file_path
        )
    else:
        s3_file_full_path = "s3://" + s3_file_path

    if IS_LOCAL:
        with open(local_file_path, "rb") as f:
            file_content = f.read()
            logger.info(
                f"Sending emulator PUT request to {s3_file_full_path} with file content (100 chars): {file_content[:100]}"
            )
            r = requests.put(s3_file_full_path, data=file_content)
            logger.info(f"Received S3 emulator response: {r.status_code}")
            if not r.ok:
                logger.error(f"S3 emulator error: {r.content}")
                error_code = 1
                raise WorkerException(
                    *get_error_by_code(error_code, worker_error_codes, logger),
                )
            return {"status": "success"}
    else:
        s3: S3Client = boto3.client("s3")  # type: ignore
        try:
            extra_args = {}
            if s3_file_path.endswith(".html"):
                extra_args = {"ContentType": "text/html"}
            ExtraArgs = extra_args if extra_args else None
            s3.upload_file(
                local_file_path,
                S3_BUCKET_NAME,
                s3_file_path,
                ExtraArgs=ExtraArgs,
            )
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error: {e}")
            logger.info(f"update submission status to {FAILED}")
            update_submission_status(submission_id, FAILED)
            error_code = 1
            raise WorkerException(
                *get_error_by_code(error_code, worker_error_codes, logger)
            )


def pull_from_s3(
    IS_LOCAL: bool,
    S3_BUCKET_NAME: str,
    s3_file_path: str,
    local_file_path: str,
    logger: logging.Logger,
) -> str:
    logger.info(f"pull file {s3_file_path} from s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        logger.info("running locally")
        s3_file_full_path = "http://s3:5000/get_object/" + s3_file_path
        # s3_file_full_path = 'http://127.0.0.1:5000/get_object/' + s3_file_path
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
        s3: S3Client = boto3.client("s3")  # type: ignore

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
    error_code: int,
    error_codes_dict: dict[str, str],
    logger: logging.Logger | None,
) -> tuple[int, str]:
    error_code_str = str(error_code)
    if error_code_str not in error_codes_dict:
        logger_if_able(
            f"Error code {error_code} not found in error codes",
            logger,
            "ERROR",
        )
        error_code_str = "500"
    return error_code, error_codes_dict[error_code_str]


def copy_file_to_directory(
    file: str,
    src_dir: str,
    dest_dir: str,
    logger: logging.Logger | None = None,
):
    src_file_path = os.path.join(src_dir, file)

    if not os.path.exists(src_file_path):
        raise FileNotFoundError(f"File {src_file_path} not found.")

    if not os.path.exists(dest_dir):
        raise FileNotFoundError(f"Directory {dest_dir} not found.")

    try:
        shutil.copy(src_file_path, dest_dir)
    except Exception as e:
        logger_if_able(
            f"Error moving file {src_file_path} to {dest_dir}", logger, "ERROR"
        )
        logger_if_able(e, logger, "ERROR")
        raise e


def move_file_to_directory(
    file: str,
    src_dir: str,
    dest_dir: str,
    logger: logging.Logger | None = None,
):
    src_file_path = os.path.join(src_dir, file)

    if not os.path.exists(src_file_path):
        raise FileNotFoundError(f"File {src_file_path} not found.")

    if not os.path.exists(dest_dir):
        raise FileNotFoundError(f"Directory {dest_dir} not found.")

    try:
        shutil.move(src_file_path, dest_dir)
    except Exception as e:
        logger_if_able(
            f"Error moving file {src_file_path} to {dest_dir}", logger, "ERROR"
        )
        logger_if_able(e, logger, "ERROR")
        raise e


# API Utility Functions

IS_LOCAL = is_local()

API_BASE_URL = (
    "http://api:8005" if IS_LOCAL else "https://api.pv-validation-hub.org"
)

S3_BASE_URL = "http://s3:5000/get_object/" if IS_LOCAL else "s3://"


def method_request(
    method: str,
    url: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: logging.Logger | None = None,
):

    logger_if_able(f"{method} request to {url}", logger)

    base_headers = {
        "Content-Type": "application/json",
    }

    all_headers: dict[str, str] = (
        {**base_headers, **headers} if headers else base_headers
    )

    body = json.dumps(data) if data else None

    response = requests.request(method, url, headers=all_headers, data=body)

    return response


def login_to_API(
    username: str, password: str, logger: logging.Logger | None = None
):

    login_url = f"{API_BASE_URL}/login"

    json_body = request_handler(
        "POST", login_url, {"username": username, "password": password}
    )

    if "token" not in json_body:
        logger_if_able("Token not in response", logger, "ERROR")
        raise Exception("Token not in response")
    token: str = json_body["token"]
    return token


def get_login_secrets_from_aws() -> tuple[str, str]:

    secret_name = "pv-validation-hub-worker-credentials"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    client: SecretsManagerClient = boto3.client(  # type: ignore
        service_name="secretsmanager", region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response["SecretString"]

    secret_dict = json.loads(secret)

    username = secret_dict.get("username", None)
    password = secret_dict.get("password", None)

    if not username or not password:
        raise Exception("Missing admin credentials")

    return username, password


def with_credentials(logger: logging.Logger | None = None):

    if IS_LOCAL:
        username = os.environ.get("admin_username", None)
        password = os.environ.get("admin_password", None)
    else:
        username, password = get_login_secrets_from_aws()

    if not username or not password:
        raise Exception("Missing admin credentials")

    api_auth_token = None
    headers = {}

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
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
    logger: logging.Logger | None = None,
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
    logger: logging.Logger | None = None,
):

    url = f"{API_BASE_URL}/{endpoint}"

    data = request_handler(method, url, data, headers, logger)
    return data


def request_to_s3(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: logging.Logger | None = None,
):

    url = f"{S3_BASE_URL}{endpoint}"

    data = request_handler(method, url, data, headers, logger)
    return data


def request_handler(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: logging.Logger | None = None,
):

    r = method_request(method, endpoint, headers=headers, data=data)
    if not r.ok:
        logger_if_able(f"Error: {r.text}", logger, "ERROR")
        raise Exception("Failed to get data")
    json_body: dict[str, Any] = json.loads(r.text)
    return json_body


# Marimo functions


def flatten_list(items: list[T]) -> list[T]:
    flat_list: list[T] = []
    for item in items:
        if isinstance(item, list):
            new_list: list[T] = flatten_list(item)  # type: ignore
            flat_list.extend(new_list)
        else:
            flat_list.append(item)
    return flat_list


def format_tuple(
    t: tuple[str, Union[int, float, str, dict[str, Any], bool, list[Any]]],
    logger: logging.Logger | None = None,
) -> str | list[str]:
    key, value = t

    logger_if_able(
        f"key: {key}, value: {value}, type: {type(value)}", logger, "DEBUG"
    )

    if isinstance(value, bool):
        return f"--{key}={str(value).lower()}"

    if isinstance(value, (int, float)):
        return f"--{key}={value}"

    if isinstance(value, str):
        if " " in [value]:
            return f'--{key}="{value}"'
        return f"--{key}={value}"

    if isinstance(value, list):
        list_args: list[str] = []
        for item in value:
            formatted_item = format_tuple((key, item))
            if isinstance(formatted_item, list):
                list_args.extend(flatten_list(formatted_item))
            if isinstance(formatted_item, str):
                list_args.append(formatted_item)
        return list_args

    if isinstance(value, dict):  # type: ignore
        try:
            json_str = json.dumps(value)
        except Exception as e:
            raise ValueError(f"Failed to convert to JSON: {e}")

        return f"--{key}={json_str}"

    raise ValueError(f"Unsupported type: {type(value)}")


def prepare_json_for_marimo_args(json_data: dict[str, Any]):

    args_list: list[str] = []

    for key, value in json_data.items():

        args = format_tuple((key, value))

        if isinstance(args, list):
            args_list.extend(flatten_list(args))
        if isinstance(args, str):
            args_list.append(args)

    return args_list


def generate_private_report_for_submission(
    df: pd.DataFrame,
    action: str,
    template_file_path: str,
    html_file_path: str,
    logger: logging.Logger | None = None,
):
    json_data: dict[str, Any] = {}
    json_data["results_df"] = df.to_dict(orient="records")  # type: ignore

    data_args_list = prepare_json_for_marimo_args(json_data)

    if not data_args_list or len(data_args_list) == 0:
        raise ValueError("No data to pass to marimo")

    logger_if_able(f"Data as args: {data_args_list}", logger, "INFO")
    logger_if_able(f"Template file path: {template_file_path}", logger, "INFO")
    logger_if_able(f"HTML file path: {html_file_path}", logger, "INFO")

    cli_commands = {
        "export": [
            "marimo",
            "export",
            "html",
            f"{template_file_path}",
            "-o",
            f"{html_file_path}",
            "--no-include-code",
            "--",
            *data_args_list,
        ],
        "edit": [
            "marimo",
            "edit",
            f"{template_file_path}",
            "--",
            *data_args_list,
        ],
        "run": [
            "marimo",
            "run",
            f"{template_file_path}",
            "--",
            *data_args_list,
        ],
    }

    if action not in cli_commands.keys():
        raise ValueError("Unsupported command")

    try:
        subprocess.run(
            cli_commands[action],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        combined_output = e.stdout + "\n" + e.stderr
        logger_if_able(f"Error: {combined_output}", logger, "ERROR")
    except Exception as e:
        logger_if_able(f"Error: {e}", logger, "ERROR")
        raise e


# Docker functions


class DockerContainerContextManager:

    def __init__(
        self,
        client: docker.DockerClient,
        image: Image | str,
        command: str | list[str],
        volumes: list[str],
        mem_limit: str | None = None,
    ) -> None:
        self.client = client
        self.container: Container | None = None
        self.id: str | None = None
        self.image = image
        self.command = command
        self.volumes = volumes
        self.mem_limit = f"{mem_limit}g" if mem_limit else None

    def __enter__(self):
        container = self.client.containers.run(
            image=self.image,
            command=self.command,
            volumes=self.volumes,
            detach=True,
            stdout=True,
            stderr=True,
            mem_limit=self.mem_limit,
        )  # type: ignore

        self.container = container

        self.id = self.container.id

        return self.container

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ):
        if self.container:
            if self.container.status == "running":
                self.container.stop()
            self.container.remove()


def docker_task(
    client: docker.DockerClient,
    image: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: tuple[Any, ...],
    data_dir: str,
    results_dir: str,
    logger: logging.Logger | None = None,
) -> tuple[bool, int | None]:

    error_raised = False
    error_code: int | None = None

    volumes = [f"{results_dir}:/app/results", f"{data_dir}:/app/data"]

    logger_if_able(f"volumes: {volumes}", logger)

    command: list[str] = [
        "python",
        "submission_wrapper.py",
        submission_file_name,
        submission_function_name,
        *submission_args,
    ]

    with DockerContainerContextManager(
        client, image, command, volumes, memory_limit
    ) as container:
        logger_if_able("Docker container starting...", logger)
        logger_if_able(f"Image: {image}", logger)
        logger_if_able(f"Submission file name: {submission_file_name}", logger)
        logger_if_able(
            f"Submission function name: {submission_function_name}", logger
        )
        logger_if_able(f"Submission args: {submission_args}", logger)

        # Wait for container to finish
        for line in container.logs(stream=True):
            line = cast(str, line)
            logger_if_able(line.strip(), logger)

        try:
            container_dict = container.wait()
        except Exception as e:
            error_raised = True
            error_code = 500
            logger_if_able(f"Error: {e}", logger, "ERROR")
            return error_raised, error_code

        if "StatusCode" not in container_dict:
            raise Exception(
                "Error: Docker container did not return status code"
            )

        exit_code = container_dict["StatusCode"]

        if exit_code != 0:
            error_raised = True
            error_code = exit_code
            logger_if_able("Error: Docker container exited with error", logger)

    return error_raised, error_code


def update_submission_progress(
    submission_id: str,
    data: dict[str, Any],
    logger: logging.Logger | None = None,
):
    result = request_to_API_w_credentials(
        "POST",
        f"submissions/submission/{submission_id}/progress_increment",
        data=data,
        logger=logger,
    )
    return result


class NonBreakingErrorReport(TypedDict):
    error_code: int
    error_type: str
    error_message: str
    file_name: str


def update_error_report_non_breaking(
    submission_id: str,
    data: NonBreakingErrorReport,
    logger: logging.Logger | None = None,
):
    result = request_to_API_w_credentials(
        "POST",
        f"error/error_report/{submission_id}/update_non_breaking",
        data=data,  # type: ignore
        logger=logger,
    )
    return result


class ErrorReport(TypedDict):
    submission: int
    error_code: str
    error_type: str
    error_message: str
    error_rate: int
    file_errors: dict[str, Any]


def create_blank_error_report(
    submission_id: int,
    logger: logging.Logger | None = None,
):
    error_report: ErrorReport = {
        "submission": submission_id,
        "error_code": "",
        "error_type": "",
        "error_message": "",
        "error_rate": 0,
        "file_errors": {"errors": []},
    }

    request_to_API_w_credentials(
        "POST", "error/error_report/new", error_report, logger=logger  # type: ignore
    )

    return error_report


def submission_task(
    submission_id: str,
    image_tag: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: tuple[Any, ...],
    data_dir: str,
    results_dir: str,
    logger: logging.Logger | None = None,
) -> tuple[bool, int | None]:

    error = False
    error_code: int | None = None
    execution_time: float | None = None

    with DockerClientContextManager() as client:
        try:
            [error_raised, error_code_raised], execution_time = timing()(
                docker_task
            )(
                client=client,
                image=image_tag,
                memory_limit=memory_limit,
                submission_file_name=submission_file_name,
                submission_function_name=submission_function_name,
                submission_args=submission_args,
                data_dir=data_dir,
                results_dir=results_dir,
                logger=logger,
            )
            if error_raised:
                error = True
                error_code = error_code_raised
                logger_if_able("Error: Docker task failed", logger, "ERROR")
        except Exception as e:
            error = True
            error_code = 500
            logger_if_able(f"Error: {e}", None, "ERROR")

    try:
        result = update_submission_progress(
            submission_id, {"file_exec_time": execution_time}, logger
        )
        logger_if_able(f"Progress update: {result}", logger)
    except Exception as e:
        # error = True
        # error_code = 500
        logger_if_able(f"Error: {e}", logger, "ERROR")

    # TODO: Send to API
    # Create an error report for all non breaking errors and send to API

    if error and error_code:
        try:
            _, error_message = get_error_by_code(
                error_code, submission_error_codes, logger
            )

            file_error_report: NonBreakingErrorReport = {
                "error_code": error_code,
                "error_type": SubmissionException.__name__,
                "error_message": error_message,
                "file_name": submission_args[0],
            }

            logger_if_able(f"Error: {file_error_report}", logger, "ERROR")
            # error, error_code = create_error_report(
            #     submission_file_name, error_code, logger
            # )
            update_error_report_non_breaking(
                submission_id, file_error_report, logger
            )
        except Exception as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")

    # # Send error report to API
    # send_error_report_to_API(json_errors, error_rate)

    return error, error_code


def is_valid_python_version(python_version: str) -> bool:
    supported_python_versions = cast(
        list[str],
        request_to_API_w_credentials("GET", "versions/python", logger=None),
    )
    return python_version in supported_python_versions


def create_docker_image(
    dir_path: str,
    tag: str,
    python_version: str,
    submission_file_name: str,
    client: docker.DockerClient,
    overwrite: bool = False,
    logger: logging.Logger | None = None,
):

    # file_path = os.path.join(os.path.dirname(__file__), "environment")

    logger_if_able(dir_path, logger)
    logger_if_able(python_version, logger)

    # Check if Dockerfile exists
    if not os.path.exists(os.path.join(dir_path, "Dockerfile")):
        raise FileNotFoundError("Dockerfile not found")

    valid_python_version = is_valid_python_version(python_version)
    if not valid_python_version:
        raise ValueError(f"Python version {python_version} is not supported")

    # Check if docker image already exists

    image = None

    if not overwrite:
        try:
            image = client.images.get(tag)
        except ImageNotFound:
            logger_if_able("Docker image not found", logger)
        except Exception as e:
            raise e

    if image:
        logger_if_able("Docker image already exists", logger)
        logger_if_able(image, logger)
        return image
    else:
        logger_if_able("Docker image does not exist", logger)

        logger_if_able("Creating Docker image", logger)

        try:
            # Create docker image from Dockerfile
            live_log_generator = client.api.build(
                path=dir_path,
                tag=tag,
                rm=True,
                nocache=True,
                dockerfile="Dockerfile",
                buildargs={
                    "zip_file": f"{submission_file_name}",
                    "python_version": python_version,
                },
            )
            image_id = None
            last_event = None
            for chunk in live_log_generator:
                logs_list = parse_docker_logs(chunk)
                for log in logs_list:
                    json_dict: dict[str, str] = json.loads(log)
                    if "error" in json_dict:
                        raise BuildError(
                            json_dict["error"].rstrip(), live_log_generator
                        )
                    if "stream" in json_dict:
                        logger_if_able(json_dict["stream"].rstrip(), logger)

                last_event = chunk
            if image_id:
                image = client.images.get(image_id)
            else:
                raise BuildError(last_event or "Unknown", live_log_generator)

            logger_if_able("Docker image created")
            return image
        except APIError as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")
            raise e
        except BuildError as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")
            raise e
        except Exception as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")
            raise e


def parse_docker_logs(input: bytes) -> list[str]:
    """
    Parses the logs from the Docker container and returns a list of strings.
    """
    logs = input.decode("utf-8")
    log_lines = logs.split("\r\n")
    parsed_logs: list[str] = []
    for line in log_lines:
        if line:
            parsed_logs.append(line.strip())
    return parsed_logs


class DockerClientContextManager:
    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = initialize_docker_client()
        return self.client

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ):
        if self.client:
            self.client.close()  # type: ignore


def initialize_docker_client():
    base_url = os.environ.get("DOCKER_HOST", None)

    client = docker.DockerClient(
        base_url=base_url,
        version="auto",
        # tls={
        #     "ca_cert": ca_cert,
        #     "client_cert": (client_cert, client_key),
        #     "verify": True,
        # },
    )
    return client


def is_docker_daemon_running():
    is_running = False

    with DockerClientContextManager() as client:
        if client.ping():  # type: ignore
            is_running = True

    return is_running


def create_docker_image_for_submission(
    dir_path: str,
    image_tag: str,
    python_version: str,
    submission_file_name: str,
    overwrite: bool = True,
    logger: logging.Logger | None = None,
):

    is_docker_daemon_running()

    with DockerClientContextManager() as client:
        try:
            image = create_docker_image(
                dir_path,
                image_tag,
                python_version,
                submission_file_name,
                client,
                overwrite=overwrite,
                logger=logger,
            )
        except Exception as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")
            raise e

    return image, image_tag
