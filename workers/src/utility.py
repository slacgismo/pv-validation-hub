import json
import shutil
from dask.delayed import delayed
from dask.distributed import Client
from dask import config
import docker
from docker.models.containers import Container
from docker.errors import ImageNotFound, BuildError
from docker.models.images import Image

from concurrent.futures import (
    ThreadPoolExecutor,
)
from logging import Logger
from time import perf_counter, sleep
import os
from typing import (
    Any,
    Callable,
    ParamSpec,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)
import logging
import boto3
import botocore.exceptions
from mypy_boto3_s3 import S3Client
import psutil
import requests
import math
import subprocess
import pandas as pd


WORKER_ERROR_PREFIX = "wr"
RUNNER_ERROR_PREFIX = "op"
SUBMISSION_ERROR_PREFIX = "sb"


T = TypeVar("T")
P = ParamSpec("P")

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


def logger_if_able(
    message: object, logger: Logger | None = None, level: str = "INFO"
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


def timeout(seconds: int, logger: Union[Logger, None] = None):
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


U = TypeVar("U")


def dask_multiprocess(
    func: Callable[P, T],
    func_arguments: Sequence[Tuple[U, ...]],
    n_workers: int | None = None,
    threads_per_worker: int | None = None,
    memory_per_run: float | int | None = None,
    logger: Logger | None = None,
    **kwargs,
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

        lazy_results = []
        for args in func_arguments:

            logger_if_able(f"args: {args}", logger, "INFO")

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


def copy_file_to_directory(
    file: str, src_dir: str, dest_dir: str, logger: Logger | None = None
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
    file: str, src_dir: str, dest_dir: str, logger: Logger | None = None
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


def get_login_secrets_from_aws() -> tuple[str, str]:

    secret_name = "pv-validation-hub-worker-credentials"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
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


def with_credentials(logger: Logger | None = None):

    if IS_LOCAL:
        username = os.environ.get("admin_username", None)
        password = os.environ.get("admin_password", None)
    else:
        username, password = get_login_secrets_from_aws()

    if not username or not password:
        raise Exception("Missing admin credentials")

    api_auth_token = None
    headers = {}

    def decorator(func: Callable[P, T]):
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


# Marimo functions


def flatten_list(items: list[T]) -> list[T]:
    flat_list: list[T] = []
    for item in items:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def format_tuple(
    t: tuple[str, Any], logger: Logger | None = None
) -> str | list[str]:
    key, value = t

    logger_if_able(
        f"key: {key}, value: {value}, type: {type(value)}", logger, "DEBUG"
    )

    if isinstance(value, (int, float)):
        return f"--{key}={value}"

    if isinstance(value, str):
        if " " in [value]:
            return f'--{key}="{value}"'
        return f"--{key}={value}"

    if isinstance(value, (dict)):
        try:
            json_str = json.dumps(value)
        except Exception as e:
            raise ValueError(f"Failed to convert to JSON: {e}")

        return f"--{key}={json_str}"

    if isinstance(value, bool):
        return f"--{key}={str(value).lower()}"

    if isinstance(value, list):
        list_args: list[str] = []
        for item in value:
            formatted_item = format_tuple((key, item))
            if isinstance(formatted_item, list):
                list_args.extend(flatten_list(formatted_item))
            if isinstance(formatted_item, str):
                list_args.append(formatted_item)
        return list_args

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
    logger: Logger | None = None,
):
    json_data: dict[str, Any] = {}
    json_data["results_df"] = df.to_dict(orient="records")

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
        volumes: dict[str, dict[str, str]] | list[str],
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
        )

        self.container = cast(Container, container)

        self.id = self.container.id

        return self.container

    def __exit__(self, exc_type, exc_value, exc_traceback):
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
    submission_args: Sequence[Any],
    data_dir: str,
    results_dir: str,
    logger: Logger | None = None,
) -> tuple[bool, int | None]:

    error_raised = False
    error_code: int | None = None

    if submission_args is None:
        submission_args = []

    # Define volumes to mount
    # results_dir = os.path.join(os.path.dirname(__file__), "results")
    # data_dir = os.path.join(os.path.dirname(__file__), "data")

    volumes = {
        results_dir: {"bind": "/app/results/", "mode": "rw"},
        data_dir: {"bind": "/app/data/", "mode": "ro"},
    }

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
            container_dict: dict[str, Any] = container.wait()
        except Exception as e:
            error_raised = True
            error_code = 500
            logger_if_able(f"Error: {e}", logger, "ERROR")
            return error_raised, error_code

        if "StatusCode" not in container_dict:
            raise Exception(
                "Error: Docker container did not return status code"
            )

        exit_code: int = cast(int, container_dict["StatusCode"])

        if exit_code != 0:
            error_raised = True
            error_code = exit_code
            logger_if_able("Error: Docker container exited with error", logger)

    return error_raised, error_code


def submission_task(
    image_tag: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: Sequence[Any],
    data_dir: str,
    results_dir: str,
    logger: Logger | None = None,
) -> tuple[bool, int | None]:

    error = False
    error_code: int | None = None

    with DockerClientContextManager() as client:
        try:
            error_raised, error_code_raised = docker_task(
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

    return error, error_code


def create_docker_image(
    dir_path: str,
    tag: str,
    submission_file_name: str,
    client: docker.DockerClient,
    overwrite: bool = False,
    logger: Logger | None = None,
):

    # file_path = os.path.join(os.path.dirname(__file__), "environment")

    logger_if_able(dir_path, logger)

    # Check if Dockerfile exists
    if not os.path.exists(os.path.join(dir_path, "Dockerfile")):
        raise FileNotFoundError("Dockerfile not found")

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
        logger_if_able("Docker image does not exist")

        try:
            # Create docker image from Dockerfile
            image, build_logs = client.images.build(
                path=dir_path,
                tag=tag,
                rm=True,
                dockerfile="Dockerfile",
                buildargs={"zip_file": f"{submission_file_name}"},
            )
            for log in build_logs:
                if "stream" in log:
                    logger_if_able(log["stream"].strip())

            logger_if_able("Docker image created")

            return image
        except BuildError as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")
            raise e
        except Exception as e:
            logger_if_able(f"Error: {e}", logger, "ERROR")
            raise e


class DockerClientContextManager:
    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = initialize_docker_client()
        return self.client

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.client:
            self.client.close()


def initialize_docker_client():
    base_url = os.environ.get("DOCKER_HOST", None)

    if not base_url:
        logger_if_able("Docker host not set", None, "WARNING")

    # cert_path = os.environ.get("DOCKER_CERT_PATH")
    # if not cert_path:
    #     raise FileNotFoundError(
    #         "DOCKER_CERT_PATH environment variable not set"
    #     )

    # if not os.path.exists(cert_path):
    #     raise FileNotFoundError(f"Cert path {cert_path} not found")

    # ca_cert = cert_path + "/ca.pem"
    # client_cert = cert_path + "/ca-key.pem"
    # client_key = cert_path + "/key.pem"

    # if not os.path.exists(ca_cert):
    #     raise FileNotFoundError(f"CA cert {ca_cert} not found")
    # if not os.path.exists(client_cert):
    #     raise FileNotFoundError(f"Client cert {client_cert} not found")
    # if not os.path.exists(client_key):
    #     raise FileNotFoundError(f"Client key {client_key} not found")

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
        if client.ping():
            is_running = True

    return is_running


def create_docker_image_for_submission(
    dir_path: str,
    image_tag: str,
    submission_file_name: str,
    overwrite: bool = True,
    logger: Logger | None = None,
):

    is_docker_daemon_running()

    with DockerClientContextManager() as client:
        image = create_docker_image(
            dir_path,
            image_tag,
            submission_file_name,
            client,
            overwrite=overwrite,
            logger=logger,
        )

    return image, image_tag


def dask_main():
    results: list = []

    total_workers = 2
    total_threads = 1
    memory_per_worker = 8

    dir_path = os.path.join(os.path.dirname(__file__), "environment")

    image_tag = "submission:latest"

    submission_file_name = "submission.zip"

    image, _ = create_docker_image_for_submission(
        dir_path, image_tag, submission_file_name
    )

    data_files = os.listdir("data")
    print(data_files)

    if not data_files:
        raise FileNotFoundError("No data files found")

    files = data_files[:5]

    submission_file_name = "submission.submission_wrapper"
    submission_function_name = "detect_time_shifts"

    data_dir = "/Users/mvicto/Desktop/Projects/PVInsight/pv-validation-hub/pv-validation-hub/dockerize-workflow/data"
    results_dir = "/Users/mvicto/Desktop/Projects/PVInsight/pv-validation-hub/pv-validation-hub/dockerize-workflow/results"

    with Client(
        n_workers=total_workers,
        threads_per_worker=total_threads,
        memory_limit=f"{memory_per_worker}GiB",
        # **kwargs,
    ) as client:

        lazy_results = []
        for file in files:
            submission_args = (file,)
            lazy_result = delayed(submission_task, pure=True)(
                image_tag,
                memory_per_worker,
                submission_file_name,
                submission_function_name,
                submission_args,
                data_dir,
                results_dir,
                logger,
            )
            lazy_results.append(lazy_result)

        futures = client.compute(lazy_results)

        results = client.gather(futures)  # type: ignore

    return results


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
