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


MEMORY_PER_RUN = 7.0  # in GB


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
        raise Exception("Could not determine number of CPUs.")

    if n_workers is not None and threads_per_worker is not None:
        if n_workers * threads_per_worker > cpu_count:
            raise Exception(
                f"workers and threads exceed local resources, {cpu_count} cores present"
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
        if thread_worker_total < 2:
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
                    "Could not determine number of workers and threads"
                )
            handle_exceeded_resources(
                n_workers, threads_per_worker, memory_per_run, sys_memory
            )

            total_workers, total_threads = n_workers, threads_per_worker
    return total_workers, total_threads


def dask_multiprocess(
    func: Callable[..., T],
    func_arguments: list[tuple[Any, ...]],
    n_workers: int | None = None,
    threads_per_worker: int | None = None,
    memory_per_run: float | int | None = None,
    logger: Logger | None = None,
    **kwargs,
):
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

    results = []

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

        results = client.gather(futures)

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
