from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import wraps
from logging import Logger
from time import perf_counter
import os
from typing import Callable, Tuple, TypeVar, Union


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
    func: Callable, data: list, n_processes: int, logger: Logger
) -> list:
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        futures = {executor.submit(func, d): d for d in data}
        results = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Error: {e}")
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
