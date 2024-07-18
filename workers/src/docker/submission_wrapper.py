from importlib import import_module
import inspect
from re import sub
import sys
import pandas as pd
import numpy as np
from time import perf_counter
from functools import wraps
from typing import Any, ParamSpec, Union, Tuple, TypeVar, Callable, cast
from logging import Logger
import logging

T = TypeVar("T")

P = ParamSpec("P")


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


def timing(verbose: bool = True, logger: Union[Logger, None] = None):
    def decorator(func: Callable[P, T]):
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


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def format_args_for_submission(
    data_dir: str, function_params: list[str], args: list[str]
):
    filename = args[0]

    file_path = f"{data_dir}/file_data/{filename}"

    df = pd.read_csv(
        file_path,
        index_col=0,
        parse_dates=True,
    )

    series: pd.Series = df.squeeze()

    rest_args = args[1:]
    new_args = []

    for arg in rest_args:
        if is_float(arg):
            new_args.append(float(arg))
        elif arg.isdigit():
            new_args.append(int(arg))
        else:
            new_args.append(arg)

    submission_args: list = [series, *new_args]

    if len(submission_args) != len(function_params):
        print(
            f"Function parameters do not match submission arguments: {submission_args}"
        )
        submission_args = submission_args[: len(function_params)]

    print(f"Submission args: {submission_args}")

    return submission_args


def import_submission_function(submission_file_name: str, function_name: str):
    # Dynamically import function from submission.py
    try:
        submission_module = import_module(submission_file_name)
    except ModuleNotFoundError as e:
        print(f"ModuleNotFoundError: {submission_file_name} not found")
        raise e

    try:
        submission_function: Callable[[pd.Series, Any], np.ndarray] = getattr(
            submission_module, function_name
        )
        function_parameters = list(
            inspect.signature(submission_function).parameters.keys()
        )
    except AttributeError as e:
        print(
            f"AttributeError: {function_name} not found in submission module"
        )
        raise e

    return submission_function, function_parameters


def main():
    args = sys.argv[1:]

    if len(args) < 1:
        print("Function name not provided")
        sys.exit(1)

    submission_file_name = args[0]
    function_name = args[1]
    data_file_name = args[2]

    print("Getting submission function...")

    try:
        submission_function, function_parameters = import_submission_function(
            submission_file_name, function_name
        )
    except AttributeError as e:
        error_code = 500
        exit(error_code)
    print("Got submission function")

    print(f"Submission file name: {submission_file_name}")
    print(f"Function name: {function_name}")
    print(f"Function: {submission_function}")
    print(f"Function parameters: {function_parameters}")

    data_dir = "/app/data"
    results_dir = "/app/results"

    submission_args = format_args_for_submission(
        data_dir, function_parameters, args[2:]
    )

    print(f"Submission args: {submission_args}")

    results, execution_time = timing()(submission_function)(*submission_args)

    print(f"Execution time: {execution_time}")

    print(f"Results: {results}")

    # save results to csv file

    print(f"Saving results to {results_dir}/{data_file_name}")

    results_df = pd.DataFrame(results)
    results_file = f"{results_dir}/{data_file_name}"
    results_df.to_csv(results_file)

    execution_tuple = (data_file_name, execution_time)
    execution_file = f"{results_dir}/time.csv"
    execution_df = pd.DataFrame([execution_tuple])
    execution_df.to_csv(execution_file, mode="a", header=False)


if __name__ == "__main__":
    main()
