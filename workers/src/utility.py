from dask.delayed import delayed
from dask.distributed import Client

from concurrent.futures import ProcessPoolExecutor, as_completed, thread
from functools import wraps
from logging import Logger
from time import perf_counter, sleep
import os
from typing import Any, Callable, Tuple, TypeVar, Union
import logging
import boto3
import botocore.exceptions
from distributed import LocalCluster
from matplotlib.pylab import f
import requests


WORKER_ERROR_PREFIX = "wr"
RUNNER_ERROR_PREFIX = "op"
SUBMISSION_ERROR_PREFIX = "sb"

T = TypeVar("T")


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
                if logger:
                    logger.info(msg)
                else:
                    print(msg)
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


def dask_multiprocess(
    func: Callable[..., T],
    func_arguments: list[tuple[Any, ...]],
    n_workers: int | None = None,
    threads_per_worker: int | None = None,
    memory_limit: str | float | int | None = None,
    logger: Logger | None = None,
) -> T | list[T] | tuple[T, ...]:

    # if n_workers is None:
    #     n_workers = os.cpu_count()
    #     if n_workers is None:
    #         msg = (
    #             "Could not determine number of CPUs. Defaulting to 4 workers."
    #         )
    #         if logger:
    #             logger.warning(msg)
    #         else:
    #             print(msg)
    #         n_workers = 4

    # if threads_per_worker is None:
    #     threads_per_worker = None

    client = Client(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit=memory_limit,
    )

    # LocalCluster()

    if logger is not None:
        print(f"logger name: {logger.name}")
        logger.info(f"Forwarding logging to dask client")
        client.forward_logging(logger.name, level=logging.INFO)

    if logger is not None:
        logger.info(f"Created dask client")
        logger.info(f"Client: {client}")
    else:
        print(f"Created dask client")
        print(f"Client: {client}")

    lazy_results = []
    for args in func_arguments:
        lazy_result = delayed(func)(*args)
        lazy_results.append(lazy_result)

    futures = client.compute(lazy_results)

    results = client.gather(futures)

    client.close()

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
