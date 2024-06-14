from importlib import import_module
import inspect
import sys
import pandas as pd
import numpy as np

from typing import Callable, cast


def format_args_for_submission(data_dir: str, args: list[str]):
    filename = args[0]

    file_path = f"{data_dir}/{filename}"

    df = pd.read_csv(
        file_path,
        index_col=0,
        parse_dates=True,
    )

    print(df.head(5))

    series: pd.Series = df.asfreq("60min").squeeze()

    submission_args = [series, *args[1:]]

    return submission_args


def import_submission_function(submission_file_name: str, function_name: str):
    # Dynamically import function from submission.py
    try:
        submission_module = import_module(submission_file_name)
    except ModuleNotFoundError as e:
        print(f"ModuleNotFoundError: {submission_file_name} not found")
        raise e

    try:
        submission_function: Callable = getattr(
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

    submission_function, function_parameters = import_submission_function(
        submission_file_name, function_name
    )
    print("Got submission function")

    print(f"Submission file name: {submission_file_name}")
    print(f"Function name: {function_name}")
    print(f"Function: {submission_function}")
    print(f"Function parameters: {function_parameters}")

    data_dir = "/app/data/"
    results_dir = "/app/results/"

    submission_args = format_args_for_submission(data_dir, args[2:])

    print(f"Submission args: {submission_args}")

    results: np.ndarray = submission_function(*submission_args)

    print(f"Results: {results}")

    # save results to csv file
    results_df = pd.DataFrame(results)
    results_file = f"{results_dir}/{data_file_name}"
    results_df.to_csv(results_file)


if __name__ == "__main__":
    main()
