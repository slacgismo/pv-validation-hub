from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import wraps
from logging import Logger
from multiprocessing import Pool
from time import perf_counter
from typing import Callable


def timing(verbose: bool = True) -> Callable:
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = perf_counter()
            result = func(*args, **kwargs)
            end_time = perf_counter()
            execution_time = end_time - start_time
            if verbose:
                print(f"{func.__name__} took {execution_time:.3f} seconds to run")
            return result, execution_time

        return wrapper

    return decorator


def multiprocess(func: Callable, data: list, n_processes: int, logger: Logger) -> list:
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        futures = {executor.submit(func, d): d for d in data}
        results = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Error: {e}")
    return results
