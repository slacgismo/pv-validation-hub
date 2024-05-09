"""
Runner script for assessing validation algorithms. In this
script, the following occurs:
    1. Pull down all of the metadata associated with the data sets
    2. Loop through all metadata cases, pull down the associated data, and
    run the associated submission on it
    3. Aggregate the results for the entire data set and generate assessment
    metrics. Assessment metrics will vary based on the type of analysis being
    run. Some examples include:
        1. Mean Absolute Error between predicted time shift series and ground
        truth time series (in minutes)
        2. Average run time for each data set (in seconds)
    4. Further aggregate performance metrics into visualizations:
        -Distribution Histograms
        -Scatter plots
      This section will be dependent on the type of analysis being run.
"""

from multiprocessing.spawn import prepare
from typing import Any, Callable, cast
import pandas as pd
import os
from importlib import import_module
import inspect
from collections import ChainMap
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json
import requests
import tarfile
import shutil
import sys
import zipfile
import subprocess
import logging
import boto3
from logger import setup_logging
from utility import (
    RunnerException,
    dask_multiprocess,
    pull_from_s3,
    timing,
    is_local,
)

FAILED = "failed"

setup_logging()

# Create a logger
logger = logging.getLogger(__name__)


IS_LOCAL = is_local()

S3_BUCKET_NAME = "pv-validation-hub-bucket"

API_BASE_URL = "api:8005" if IS_LOCAL else "api.pv-validation-hub.org"


def push_to_s3(
    local_file_path,
    s3_file_path,
    analysis_id,
    submission_id,
    update_submission_status,
):
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        s3_file_full_path = (
            "http://s3:5000/put_object/" + S3_BUCKET_NAME + "/" + s3_file_path
        )
    else:
        s3_file_full_path = "s3://" + s3_file_path

    if IS_LOCAL:
        with open(local_file_path, "rb") as f:
            file_content = f.read()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                logger.error(
                    f"error put file {s3_file_path} to s3, status code {r.status_code} {r.content}"
                )
                logger.info(f"update submission status to {FAILED}")
                update_submission_status(analysis_id, submission_id, FAILED)
    else:
        s3 = boto3.client("s3")
        s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_path)


def convert_compressed_file_path_to_directory(compressed_file_path):
    path_components = compressed_file_path.split("/")
    path_components[-1] = path_components[-1].split(".")[0]
    path_components = "/".join(path_components)
    return path_components


def extract_files(  # noqa: C901
    ref: zipfile.ZipFile | tarfile.TarFile,
    extract_path: str,
    zip_path: str,
    remove_unallowed_starting_characters: Callable[[str], str | None],
):

    logger.info("Extracting files from: " + zip_path)

    if ref.__class__ == zipfile.ZipFile:
        ref = cast(zipfile.ZipFile, ref)
        file_names = ref.namelist()
    elif ref.__class__ == tarfile.TarFile:
        ref = cast(tarfile.TarFile, ref)
        file_names = ref.getnames()
    else:
        raise Exception("File is not a zip or tar file.")

    # recursively remove files and folders that start with certain characters
    file_names = [
        f for f in file_names if remove_unallowed_starting_characters(f)
    ]
    logger.info("File names:")
    logger.info(file_names)
    folders = [f for f in file_names if f.endswith("/")]
    logger.info("Folders:")
    logger.info(folders)

    if len(folders) == 0:
        logger.info("Extracting all files...")

        for file in file_names:
            if ref.__class__ == zipfile.ZipFile:
                ref = cast(zipfile.ZipFile, ref)
                ref.extract(file, path=extract_path)
            elif ref.__class__ == tarfile.TarFile:
                ref = cast(tarfile.TarFile, ref)
                ref.extract(file, path=extract_path, filter="data")
            else:
                raise Exception("File is not a zip or tar file.")

    else:
        # if all files have the same root any folder can be used to check since all will have the same root if true
        do_all_files_have_same_root = all(
            [f.startswith(folders[0]) for f in file_names]
        )
        logger.info(
            "Do all files have the same root? "
            + str(do_all_files_have_same_root)
        )

        if do_all_files_have_same_root:
            # extract all files within the folder with folder of the zipfile that has the same root
            root_folder_name = folders[0]

            logger.info("Extracting files...")
            for file in file_names:
                if file.endswith("/") and file != root_folder_name:
                    os.makedirs(
                        os.path.join(
                            extract_path,
                            file.removeprefix(root_folder_name),
                        )
                    )
                if not file.endswith("/"):
                    if ref.__class__ == zipfile.ZipFile:
                        ref = cast(zipfile.ZipFile, ref)
                        ref.extract(file, path=extract_path)
                    elif ref.__class__ == tarfile.TarFile:
                        ref = cast(tarfile.TarFile, ref)
                        ref.extract(file, path=extract_path, filter="data")
                    else:
                        raise Exception(1, "File is not a zip or tar file.")

                    os.rename(
                        os.path.join(extract_path, file),
                        os.path.join(
                            extract_path,
                            file.removeprefix(root_folder_name),
                        ),
                    )

            # remove the root folder and all other folders
            shutil.rmtree(os.path.join(extract_path, root_folder_name))

        else:
            logger.info("Extracting all files...")
            for file in file_names:
                if ref.__class__ == zipfile.ZipFile:
                    ref = cast(zipfile.ZipFile, ref)
                    ref.extract(file, path=extract_path)
                elif ref.__class__ == tarfile.TarFile:
                    ref = cast(tarfile.TarFile, ref)
                    ref.extract(file, path=extract_path, filter="data")
                else:
                    raise Exception(1, "File is not a zip or tar file.")


def extract_zip(zip_path: str, extract_path: str):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    def remove_unallowed_starting_characters(file_name: str) -> str | None:
        unallowed_starting_characters = ("_", ".")

        parts = file_name.split("/")
        for part in parts:
            if part.startswith(unallowed_starting_characters):
                return None
        return file_name

    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            extract_files(
                zip_ref,
                extract_path,
                zip_path,
                remove_unallowed_starting_characters,
            )
    elif tarfile.is_tarfile(zip_path):
        with tarfile.open(zip_path, "r") as tar_ref:
            extract_files(
                tar_ref,
                extract_path,
                zip_path,
                remove_unallowed_starting_characters,
            )
    else:
        raise Exception(1, "File is not a zip or tar file.")


def get_module_file_name(module_dir: str):
    for root, _, files in os.walk(module_dir, topdown=True):
        for name in files:
            if name.endswith(".py"):
                return name.split("/")[-1]
    else:
        raise FileNotFoundError(
            "No python file found in the module directory."
        )


def get_module_name(module_dir: str):
    return get_module_file_name(module_dir)[:-3]


def generate_histogram(
    dataframe, x_axis, title, color_code=None, number_bins=30
):
    """
    Generate a histogram for a distribution. Option to color code the
    histogram by the color_code column parameter.
    """
    sns.displot(
        dataframe, x=x_axis, hue=color_code, multiple="stack", bins=number_bins
    )
    plt.title(title)
    plt.tight_layout()
    return plt


def generate_scatter_plot(dataframe, x_axis, y_axis, title):
    """
    Generate a scatterplot between an x- and a y-variable.
    """
    sns.scatterplot(data=dataframe, x=x_axis, y=y_axis)
    plt.title(title)
    plt.tight_layout()
    return plt


@timing(verbose=True, logger=logger)
def run_user_submission(
    fn: Callable[..., pd.Series],
    *args: Any,
    **kwargs: Any,
):
    return fn(*args, **kwargs)


def run(  # noqa: C901
    s3_submission_zip_file_path: str,
    file_metadata_df: pd.DataFrame,
    update_submission_status: Callable,
    analysis_id: int,
    submission_id: int,
    current_evaluation_dir: str | None = None,
    tmp_dir: str | None = None,
) -> dict[str, Any]:
    # If a path is provided, set the directories to that path, otherwise use default
    if current_evaluation_dir is not None:
        results_dir = (
            current_evaluation_dir + "/results"
            if not current_evaluation_dir.endswith("/")
            else current_evaluation_dir + "results"
        )
        data_dir = (
            current_evaluation_dir + "/data"
            if not current_evaluation_dir.endswith("/")
            else current_evaluation_dir + "data"
        )
        sys.path.append(
            current_evaluation_dir
        )  # append current_evaluation_dir to sys.path
    else:
        results_dir = "./results"
        data_dir = "./data"
        current_evaluation_dir = os.getcwd()

    if tmp_dir is None:
        tmp_dir = "/tmp"

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Ensure results directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Load in the module that we're going to test on.
    logger.info(f"module_to_import_s3_path: {s3_submission_zip_file_path}")
    target_module_compressed_file_path = pull_from_s3(
        IS_LOCAL, S3_BUCKET_NAME, s3_submission_zip_file_path, tmp_dir, logger
    )
    logger.info(
        f"target_module_compressed_file_path: {target_module_compressed_file_path}"
    )
    target_module_path = convert_compressed_file_path_to_directory(
        target_module_compressed_file_path
    )
    logger.info(
        f"decompressing file {target_module_compressed_file_path} to {target_module_path}"
    )

    extract_zip(target_module_compressed_file_path, target_module_path)
    logger.info(
        f"decompressed file {target_module_compressed_file_path} to {target_module_path}"
    )

    logger.info(f"target_module_path: {target_module_path}")
    # get current directory, i.e. directory of runner.py file
    new_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"new_dir: {new_dir}")

    submission_file_name = get_module_file_name(target_module_path)
    logger.info(f"file_name: {submission_file_name}")
    module_name = get_module_name(target_module_path)
    logger.info(f"module_name: {module_name}")

    # install submission dependency
    try:
        subprocess.check_call(
            [
                "python",
                "-m",
                "pip",
                "install",
                "-r",
                os.path.join(target_module_path, "requirements.txt"),
            ]
        )
        logger.info("submission dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error("error installing submission dependencies:", e)
        logger.info(f"update submission status to {FAILED}")
        update_submission_status(analysis_id, submission_id, FAILED)
        raise RunnerException(
            2, "error installing python submission dependencies"
        )

    shutil.move(
        os.path.join(target_module_path, submission_file_name),
        os.path.join(new_dir, submission_file_name),
    )

    # Generate list for us to store all of our results for the module
    results_list = list()
    # Load in data set that we're going to analyze.

    # Make GET requests to the Django API to get the system metadata
    # http://api.pv-validation-hub.org/system_metadata/systemmetadata/
    smd_url = f"http://{API_BASE_URL}/system_metadata/systemmetadata/"
    system_metadata_response = requests.get(smd_url)

    if not system_metadata_response.ok:
        logger.error(
            f"Failed to get system metadata from {smd_url}: {system_metadata_response.content}"
        )
        logger.info(f"update submission status to {FAILED}")
        update_submission_status(analysis_id, submission_id, FAILED)
        raise RunnerException(3, "Failed to get system metadata information")

    # Convert the responses to DataFrames

    # System metadata: This CSV represents the system_metadata table, which is
    # a master table for associated system metadata (system_id, name, azimuth,
    # tilt, etc.)
    system_metadata_df = pd.DataFrame(system_metadata_response.json())

    if system_metadata_df.empty:
        logger.error("System metadata is empty")
        logger.info(f"update submission status to {FAILED}")
        update_submission_status(analysis_id, submission_id, FAILED)
        raise RunnerException(4, "No system metadata returned from API")

    # Read in the configuration JSON for the particular run
    with open(os.path.join(current_evaluation_dir, "config.json")) as f:
        if not f:
            logger.error("config.json not found")
            logger.info(f"update submission status to {FAILED}")
            update_submission_status(analysis_id, submission_id, FAILED)
            raise RunnerException(
                5, "config.json not found in current evaluation directory"
            )
        config_data: dict[str, Any] = json.load(f)

    # Get the associated metrics we're supposed to calculate
    performance_metrics: list[str] = config_data["performance_metrics"]
    logger.info(f"performance_metrics: {performance_metrics}")

    # Get the name of the function we want to import associated with this
    # test
    function_name: str = config_data["function_name"]
    # Import designated module via importlib
    module = import_module(module_name)
    try:
        submission_function: Callable = getattr(module, function_name)
        function_parameters = list(
            inspect.signature(submission_function).parameters
        )
    except AttributeError:
        logger.error(
            f"function {function_name} not found in module {module_name}"
        )
        logger.info(f"update submission status to {FAILED}")
        update_submission_status(analysis_id, submission_id, FAILED)
        raise RunnerException(
            6, f"function {function_name} not found in module {module_name}"
        )

    total_number_of_files = len(file_metadata_df)
    logger.info(f"total_number_of_files: {total_number_of_files}")

    number_of_errors = 0

    FAILURE_CUTOFF = 3

    def current_error_rate(number_of_errors: int, index: int):
        return (number_of_errors / (index + 1)) * 100

    # Loop through each file and generate predictions

    results_list = loop_over_files_and_generate_results(
        file_metadata_df,
        system_metadata_df,
        data_dir,
        config_data,
        submission_function,
        function_parameters,
        number_of_errors,
        function_name,
        performance_metrics,
    )
    # Convert the results to a pandas dataframe and perform all of the
    # post-processing in the script
    results_df = pd.DataFrame(results_list)
    logger.info(f"results_df: {results_df}")
    # Build out the final processed results:
    #   1) Public reporting: mean MAE, mean run time, etc.
    #   2) Private reporting: graphics and tables split by different factors
    # First get mean value for all the performance metrics and save (this will
    # be saved to a public metrics dictionary)
    public_metrics_dict: dict[str, Any] = dict()
    public_metrics_dict["module"] = module_name
    # Get the mean and median run times
    public_metrics_dict["mean_run_time"] = results_df["run_time"].mean()
    public_metrics_dict["median_run_time"] = results_df["run_time"].median()
    public_metrics_dict["function_parameters"] = function_parameters

    # Get the mean and median absolute errors
    # when combining the metric and name for the public metrics dictionary,
    # do not add anything to them. mean_mean_average_error and median_mean_average_error
    # are valid keys, anything else breaks our results processing
    for metric in performance_metrics:
        if "absolute_error" in metric:
            for val in config_data["ground_truth_compare"]:
                logger.info(
                    f"metric: {metric}, val: {val}, combined: {'mean_' + metric}"
                )
                public_metrics_dict["mean_" + metric] = results_df[
                    metric + "_" + val
                ].mean()
                public_metrics_dict["median_" + metric] = results_df[
                    metric + "_" + val
                ].median()
    # Write public metric information to a public results table.
    with open(
        os.path.join(results_dir, config_data["public_results_table"]), "w"
    ) as fp:
        json.dump(public_metrics_dict, fp)

    logger.info(f"public_metrics_dict: {public_metrics_dict}")
    # Now generate private results. These will be more specific to the
    # type of analysis being run as results will be color-coded by certain
    # parameters. These params will be available as columns in the
    # 'associated_files' dataframe
    results_df_private = pd.merge(results_df, file_metadata_df, on="file_name")
    # Filter to only the necessary columns (available via the config)
    results_df_private = results_df_private[
        config_data["private_results_columns"]
    ]
    results_df_private.to_csv(
        os.path.join(results_dir, module_name + "_full_results.csv")
    )
    # Loop through all of the plot dictionaries and generate plots and
    # associated tables for reporting
    for plot in config_data["plots"]:
        if plot["type"] == "histogram":
            if "color_code" in plot:
                color_code = plot["color_code"]
            else:
                color_code = None
            gen_plot = generate_histogram(
                results_df_private, plot["x_val"], plot["title"], color_code
            )
            # Save the plot
            gen_plot.savefig(os.path.join(results_dir, plot["save_file_path"]))
            plt.close()
            plt.clf()
            # Write the stratified results to a table for private reporting
            # (if color_code param is not None)
            if color_code:
                stratified_results_tbl = pd.DataFrame(
                    results_df_private.groupby(color_code)[
                        plot["x_val"]
                    ].mean()
                )
                stratified_results_tbl.to_csv(
                    os.path.join(
                        results_dir,
                        module_name
                        + "_"
                        + str(color_code)
                        + "_"
                        + plot["x_val"]
                        + ".csv",
                    )
                )
        if plot["type"] == "scatter_plot":
            gen_plot = generate_scatter_plot(
                results_df_private, plot["x_val"], plot["y_val"], plot["title"]
            )
            # Save the plot
            gen_plot.savefig(os.path.join(results_dir, plot["save_file_path"]))
            plt.close()
            plt.clf()

    logger.info(f"number_of_errors: {number_of_errors}")

    success_rate = (
        (total_number_of_files - number_of_errors) / total_number_of_files
    ) * 100
    logger.info(f"success_rate: {success_rate}%")
    logger.info(
        f"{total_number_of_files - number_of_errors} out of {total_number_of_files} files processed successfully"
    )

    return public_metrics_dict


def create_function_args_for_file(
    file_metadata_row: pd.Series,
    system_metadata_df: pd.DataFrame,
    data_dir: str,
    config_data: dict[str, Any],
    submission_function: Callable[..., pd.Series],
    function_parameters: list[str],
    number_of_errors: int,
    function_name: str,
    performance_metrics: list[str],
    file_number: int,
):

    file_name: str = file_metadata_row["file_name"]

    # Get associated system ID
    system_id = file_metadata_row["system_id"]

    # Get all of the associated metadata for the particular file based
    # on its system ID. This metadata will be passed in via kwargs for
    # any necessary arguments
    associated_system_metadata: dict[str, Any] = dict(
        system_metadata_df[system_metadata_df["system_id"] == system_id].iloc[
            0
        ]
    )

    function_args = (
        file_name,
        data_dir,
        associated_system_metadata,
        config_data,
        submission_function,
        function_parameters,
        file_metadata_row,
        number_of_errors,
        function_name,
        performance_metrics,
        file_number,
    )

    return function_args


def prepare_function_args_for_parallel_processing(
    file_metadata_df: pd.DataFrame,
    system_metadata_df: pd.DataFrame,
    data_dir: str,
    config_data: dict[str, Any],
    submission_function: Callable[..., pd.Series],
    function_parameters: list[str],
    number_of_errors: int,
    function_name: str,
    performance_metrics: list[str],
):
    # logger.debug(
    #     f"index: {index}, FAILURE_CUTOFF: {FAILURE_CUTOFF}, number_of_errors: {number_of_errors}"
    # )
    # if index <= FAILURE_CUTOFF:
    #     if number_of_errors == FAILURE_CUTOFF:
    #         raise RunnerException(
    #             7,
    #             f"Too many errors ({number_of_errors}) occurred in the first {FAILURE_CUTOFF} files. Exiting.",
    #             current_error_rate(number_of_errors, index),
    #         )

    # logger.info(f"processing file {index + 1} of {total_number_of_files}")

    function_args_list: list[tuple] = []

    for file_number, (_, file_metadata_row) in enumerate(
        file_metadata_df.iterrows()
    ):

        function_args = create_function_args_for_file(
            file_metadata_row,
            system_metadata_df,
            data_dir,
            config_data,
            submission_function,
            function_parameters,
            number_of_errors,
            function_name,
            performance_metrics,
            file_number,
        )
        function_args_list.append(function_args)

    return function_args_list


def run_submission(
    file_name: str,
    data_dir: str,
    associated_metadata: dict[str, Any],
    config_data: dict[str, Any],
    submission_function: Callable[..., pd.Series],
    function_parameters: list[str],
    row: pd.Series,
):

    logger.info(f"file_name: {file_name}")

    # Create master dictionary of all possible function kwargs
    kwargs = prepare_kwargs_for_submission_function(
        config_data, function_parameters, row, associated_metadata
    )

    # Now that we've collected all of the information associated with the
    # test, let's read in the file as a pandas dataframe (this data
    # would most likely be stored in an S3 bucket)
    time_series = prepare_time_series(data_dir, file_name, row)

    # Run the routine (timed)
    logger.info(
        f"running function {submission_function.__name__} with kwargs {kwargs}"
    )

    data_outputs, function_run_time = run_user_submission(
        submission_function, time_series, **kwargs
    )

    return (
        data_outputs,
        function_run_time,
    )


def loop_over_files_and_generate_results(
    file_metadata_df: pd.DataFrame,
    system_metadata_df: pd.DataFrame,
    data_dir: str,
    config_data: dict[str, Any],
    submission_function: Callable[..., pd.Series],
    function_parameters: list[str],
    number_of_errors: int,
    function_name: str,
    performance_metrics: list[str],
):

    func_arguments_list = prepare_function_args_for_parallel_processing(
        file_metadata_df,
        system_metadata_df,
        data_dir,
        config_data,
        submission_function,
        function_parameters,
        number_of_errors,
        function_name,
        performance_metrics,
    )

    results = dask_multiprocess(
        run_submission_and_generate_performance_metrics,
        func_arguments_list,
        n_workers=2,
        threads_per_worker=1,
        memory_limit="16GiB",
        logger=logger,
    )
    return results


def generate_performance_metrics_for_submission(
    data_outputs: pd.Series,
    function_run_time: float,
    file_name: str,
    data_dir: str,
    associated_metadata: dict[str, Any],
    config_data: dict[str, Any],
    function_parameters: list[str],
    number_of_errors: int,
    performance_metrics: list[str],
):
    # Get the ground truth scalars that we will compare to
    ground_truth_dict = dict()
    if config_data["comparison_type"] == "scalar":
        for val in config_data["ground_truth_compare"]:
            ground_truth_dict[val] = associated_metadata[val]
    if config_data["comparison_type"] == "time_series":
        ground_truth_series: pd.Series = pd.read_csv(
            os.path.join(data_dir + "/validation_data/", file_name),
            index_col=0,
            parse_dates=True,
        ).squeeze()
        ground_truth_dict["time_series"] = ground_truth_series

    ground_truth_file_length = len(ground_truth_series)

    file_submission_result_length = len(data_outputs)
    if file_submission_result_length != ground_truth_file_length:
        logger.error(
            f"{file_name} submission result length {file_submission_result_length} does not match ground truth file length {ground_truth_file_length}"
        )

        number_of_errors += 1
        raise RunnerException(
            100,
            f"submission result length {file_submission_result_length} does not match ground truth file length {ground_truth_file_length}",
        )

    # Convert the data outputs to a dictionary identical to the
    # ground truth dictionary
    output_dictionary: dict[str, Any] = dict()
    if config_data["comparison_type"] == "scalar":
        for idx in range(len(config_data["ground_truth_compare"])):
            output_dictionary[config_data["ground_truth_compare"][idx]] = (
                data_outputs[idx]
            )
    if config_data["comparison_type"] == "time_series":
        output_dictionary["time_series"] = data_outputs
    # Run routine for all of the performance metrics and append
    # results to the dictionary
    results_dictionary: dict[str, Any] = dict()
    results_dictionary["file_name"] = file_name
    # Set the runtime in the results dictionary
    results_dictionary["run_time"] = function_run_time
    # Set the data requirements in the dictionary
    results_dictionary["data_requirements"] = function_parameters
    # Loop through the rest of the performance metrics and calculate them
    # (this predominantly applies to error metrics)
    for metric in performance_metrics:
        if metric == "absolute_error":
            # Loop through the input and the output dictionaries,
            # and calculate the absolute error
            for val in config_data["ground_truth_compare"]:
                error = np.abs(output_dictionary[val] - ground_truth_dict[val])
                results_dictionary[metric + "_" + val] = error
        elif metric == "mean_absolute_error":
            for val in config_data["ground_truth_compare"]:
                error = np.mean(
                    np.abs(output_dictionary[val] - ground_truth_dict[val])
                )
                results_dictionary[metric + "_" + val] = error
    logger.info(f"results_dictionary: {results_dictionary}")
    return results_dictionary


def run_submission_and_generate_performance_metrics(
    file_name: str,
    data_dir: str,
    associated_system_metadata: dict[str, Any],
    config_data: dict[str, Any],
    submission_function: Callable[..., pd.Series],
    function_parameters: list[str],
    file_metadata_row: pd.Series,
    number_of_errors: int,
    function_name: str,
    performance_metrics: list[str],
    file_number: int,
):
    logger.info(f"{file_number} - running submission for file {file_name}")
    try:
        # Get file_name, which will be pulled from database or S3 for
        # each analysis
        (
            data_outputs,
            function_run_time,
        ) = run_submission(
            file_name,
            data_dir,
            associated_system_metadata,
            config_data,
            submission_function,
            function_parameters,
            file_metadata_row,
        )

    except Exception as e:
        logger.error(f"error running function {function_name}: {e}")
        number_of_errors += 1

    results_dictionary = generate_performance_metrics_for_submission(
        data_outputs,
        function_run_time,
        file_name,
        data_dir,
        associated_system_metadata,
        config_data,
        function_parameters,
        number_of_errors,
        performance_metrics,
    )

    return results_dictionary


def prepare_kwargs_for_submission_function(
    config_data: dict[str, Any],
    function_parameters: list[str],
    row: pd.Series,
    associated_metadata: dict[str, Any],
):
    kwargs_dict = dict(ChainMap(dict(row), associated_metadata))
    # Filter out to only allowable args for the function
    kwargs_dict = {
        key: kwargs_dict[key] for key in config_data["allowable_kwargs"]
    }

    # Filter the kwargs dictionary based on required function params
    kwargs: dict[str, Any] = dict(
        (k, kwargs_dict[k]) for k in function_parameters if k in kwargs_dict
    )

    return kwargs


def prepare_time_series(
    data_dir: str, file_name: str, row: pd.Series
) -> pd.Series:
    time_series_df: pd.DataFrame = pd.read_csv(
        os.path.join(data_dir + "/file_data/", file_name),
        index_col=0,
        parse_dates=True,
    )

    time_series: pd.Series = time_series_df.asfreq(
        str(row["data_sampling_frequency"]) + "min"
    ).squeeze()

    return time_series


if __name__ == "__main__":
    pass
    # run(
    #     "submission_files/submission_user_1/submission_118/dfec718f-bb6e-4194-98cf-2edea6f3f717_sdt-submission.zip",
    #     "/root/worker/current_evaluation",
    # )
    # push_to_s3(
    #     "/pv-validation-hub-bucket/submission_files/submission_user_1/submission_1/results/time-shift-public-metrics.json",
    #     "pv-validation-hub-bucket/test_bucket/test_subfolder/res.json",
    # )
