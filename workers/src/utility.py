import sys
from dask.delayed import delayed
from dask.distributed import Client
from dask import config

from concurrent.futures import ProcessPoolExecutor, as_completed, thread
from functools import wraps
from logging import Logger
from time import perf_counter, sleep, time
import os
from typing import Any, Callable, Tuple, TypeVar, Union
import logging
import boto3
import botocore.exceptions
from distributed import LocalCluster
import psutil
import requests
import math


WORKER_ERROR_PREFIX = "wr"
RUNNER_ERROR_PREFIX = "op"
SUBMISSION_ERROR_PREFIX = "sb"

T = TypeVar("T")


def timing(verbose: bool = True, logger: Union[Logger, None] = None):
    @wraps(timing)
    def decorator(func: Callable[..., T]):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[T, float]:
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
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
    memory_limit: float | int | None = None,
    logger: Logger | None = None,
    **kwargs,
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

    # if n_workers is None:
    #     n_workers = cpu_count
    # if n_workers * n_processes > cpu_count:
    #     raise Exception(f"workers and threads exceed local resources, {cpu_count} cores present")
    # if n_workers * memory_limit > sys_memory:
    #     config.set({'distributed.worker.memory.spill': True})
    #     print(f"Memory per worker exceeds system memory ({memory_limit} GB), activating memory spill\n")

    memory_limit = memory_limit or 7.0

    cpu_count = os.cpu_count()
    # memory limit in GB
    sys_memory = psutil.virtual_memory().total / (1024.0**3)

    if cpu_count is None:
        raise Exception("Could not determine number of CPUs.")

    if n_workers is not None and threads_per_worker is not None:
        if n_workers * threads_per_worker > cpu_count:
            raise Exception(
                f"workers and threads exceed local resources, {cpu_count} cores present"
            )
        if memory_limit * n_workers * threads_per_worker > sys_memory:
            config.set({"distributed.worker.memory.spill": True})
            print(
                f"Memory per worker exceeds system memory ({memory_limit} GB), activating memory spill\n"
            )

    if n_workers is not None and threads_per_worker is None:
        threads_per_worker = int(
            math.floor(sys_memory / (memory_limit * n_workers))
        )
        if threads_per_worker == 0:
            print(
                "Not enough memory for a worker, defaulting to 1 thread per worker"
            )
            threads_per_worker = 1

    if n_workers is None and threads_per_worker is not None:
        n_workers = int(
            math.floor(sys_memory / (memory_limit * threads_per_worker))
        )
        if n_workers == 0:
            print("Not enough memory for a worker, defaulting to 1 worker")
            n_workers = 1

    if n_workers is None and threads_per_worker is None:
        if memory_limit == 0:
            raise Exception("Memory limit cannot be 0")
        thread_worker_total = sys_memory / memory_limit
        if thread_worker_total < 2:
            print(
                "Not enough memory for a worker, defaulting to 1 worker and 1 thread per worker"
            )
            n_workers = 1
            threads_per_worker = 1
            if memory_limit * n_workers > sys_memory:
                config.set({"distributed.worker.memory.spill": True})
                print(
                    f"Memory per worker exceeds system memory ({memory_limit} GB), activating memory spill\n"
                )
        else:
            print(f"thread_worker_total: {thread_worker_total}")
            n_workers = int(math.floor(thread_worker_total / 2))
            threads_per_worker = int(math.floor(thread_worker_total / 2))

    # config.set({"distributed.worker.memory.spill": True})
    config.set({"distributed.worker.memory.pause": True})
    config.set({"distributed.worker.memory.target": 0.95})
    config.set({"distributed.worker.memory.terminate": False})

    print(f"cpu count: {cpu_count}")
    print(f"memory: {sys_memory}")
    print(f"memory limit per worker: {memory_limit}")
    print(f"n_workers: {n_workers}")
    print(f"threads_per_worker: {threads_per_worker}")

    client = Client(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit=f"{memory_limit}GiB",
        **kwargs,
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
        lazy_result = delayed(func, pure=True)(*args)
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
