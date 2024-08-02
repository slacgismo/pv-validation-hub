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

from typing import Any, Callable, Sequence, Tuple, TypeVar, cast, ParamSpec
import pandas as pd
import os
from importlib import import_module
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
    RUNNER_ERROR_PREFIX,
    RunnerException,
    SubmissionException,
    create_docker_image_for_submission,
    dask_multiprocess,
    generate_private_report_for_submission,
    get_error_by_code,
    get_error_codes_dict,
    move_file_to_directory,
    pull_from_s3,
    request_to_API_w_credentials,
    submission_task,
    timeout,
    timing,
    is_local,
)

P = ParamSpec("P")

FAILED = "failed"

setup_logging()

# Create a logger
logger = logging.getLogger(__name__)


IS_LOCAL = is_local()

S3_BUCKET_NAME = "pv-validation-hub-bucket"

API_BASE_URL = "api:8005" if IS_LOCAL else "api.pv-validation-hub.org"

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


runner_error_codes = get_error_codes_dict(
    FILE_DIR, RUNNER_ERROR_PREFIX, logger
)

SUBMISSION_TIMEOUT = 30 * 60  # seconds


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
                update_submission_status(submission_id, FAILED)
    else:
        s3 = boto3.client("s3")  # type: ignore
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
    fn: Callable[P, pd.Series],
    *args,
    **kwargs,
):
    return fn(*args, **kwargs)


def move_files_to_directory(files: list[str], src_dir: str, dest_dir: str):
    for file in files:
        src_file_path = os.path.join(src_dir, file)

        shutil.move(src_file_path, dest_dir)


def run(  # noqa: C901
    s3_submission_zip_file_path: str,
    file_metadata_df: pd.DataFrame,
    update_submission_status: Callable[[int, str], dict[str, Any]],
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
        docker_dir = (
            current_evaluation_dir + "/docker"
            if not current_evaluation_dir.endswith("/")
            else current_evaluation_dir + "docker"
        )

        sys.path.append(
            current_evaluation_dir
        )  # append current_evaluation_dir to sys.path
    else:
        results_dir = "./results"
        data_dir = "./data"
        docker_dir = "./docker"
        current_evaluation_dir = os.getcwd()

    if tmp_dir is None:
        tmp_dir = "/tmp"

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Ensure results directory exists
    os.makedirs(data_dir, exist_ok=True)

    # # Load in the module that we're going to test on.
    # target_module_path, new_dir, submission_file_name, module_name = install_module_dependencies(s3_submission_zip_file_path, update_submission_status, submission_id, tmp_dir)

    logger.info(f"module_to_import_s3_path: {s3_submission_zip_file_path}")
    target_module_compressed_file_path = pull_from_s3(
        IS_LOCAL, S3_BUCKET_NAME, s3_submission_zip_file_path, tmp_dir, logger
    )
    logger.info(
        f"target_module_compressed_file_path: {target_module_compressed_file_path}"
    )

    # Move the submission file to the docker directory

    submission_file_name = target_module_compressed_file_path.split("/")[-1]

    # Move the submission file to the docker directory
    move_file_to_directory(submission_file_name, tmp_dir, docker_dir)

    # raise RunnerException(*get_error_by_code(500, runner_error_codes, logger))

    # Create docker image for the submission
    image_tag = "submission:latest"

    overwrite = True

    logger.info(f"Creating docker image for submission...")

    image, image_tag = create_docker_image_for_submission(
        docker_dir, image_tag, submission_file_name, overwrite, logger
    )

    logger.info(f"Created docker image for submission: {image_tag}")

    # shutil.move(
    #     os.path.join(target_module_path, submission_file_name),
    #     os.path.join(new_dir, submission_file_name),
    # )

    # Generate list for us to store all of our results for the module
    results_list = list()
    # Load in data set that we're going to analyze.

    # Make GET requests to the Django API to get the system metadata
    # http://api.pv-validation-hub.org/system_metadata/systemmetadata/
    smd_url = f"system_metadata/systemmetadata/"
    system_metadata_json = {}

    try:
        system_metadata_json = request_to_API_w_credentials("GET", smd_url)

    except Exception as e:
        logger.error(f"Failed to get system metadata from API")
        logger.exception(e)

        logger.info(f"update submission status to {FAILED}")
        update_submission_status(submission_id, FAILED)
        error_code = 3
        raise RunnerException(
            *get_error_by_code(error_code, runner_error_codes, logger)
        )

    # Convert the responses to DataFrames

    # System metadata: This CSV represents the system_metadata table, which is
    # a master table for associated system metadata (system_id, name, azimuth,
    # tilt, etc.)
    system_metadata_df = pd.DataFrame(system_metadata_json)

    if system_metadata_df.empty:
        logger.error("System metadata is empty")
        logger.info(f"update submission status to {FAILED}")
        update_submission_status(submission_id, FAILED)
        error_code = 4
        raise RunnerException(
            *get_error_by_code(error_code, runner_error_codes, logger)
        )

    # Save system metadata to a CSV file
    system_metadata_file_name = "system_metadata.csv"

    system_metadata_df.to_csv(
        os.path.join(
            os.path.join(data_dir, "metadata"), system_metadata_file_name
        )
    )

    file_metadata_file_name = "file_metadata.csv"

    file_metadata_df.to_csv(
        os.path.join(
            os.path.join(data_dir, "metadata"), file_metadata_file_name
        )
    )

    # exit()

    # Read in the configuration JSON for the particular run
    with open(os.path.join(current_evaluation_dir, "config.json"), "r") as f:
        if not f:
            logger.error("config.json not found")
            logger.info(f"update submission status to {FAILED}")
            update_submission_status(submission_id, FAILED)
            error_code = 5
            raise RunnerException(
                *get_error_by_code(error_code, runner_error_codes, logger)
            )
        config_data: dict[str, Any] = json.load(f)

    # Get the associated metrics we're supposed to calculate
    performance_metrics: list[str] = config_data["performance_metrics"]
    logger.info(f"performance_metrics: {performance_metrics}")

    # Get the name of the function we want to import associated with this
    # test
    # # Import designated module via importlib
    # module = import_module(module_name)
    # try:
    #     submission_function: Callable = getattr(module, function_name)
    #     function_parameters = list(
    #         inspect.signature(submission_function).parameters
    #     )
    # except AttributeError:
    #     logger.error(
    #         f"function {function_name} not found in module {module_name}"
    #     )
    #     logger.info(f"update submission status to {FAILED}")
    #     update_submission_status(submission_id, FAILED)
    #     error_code = 6
    #     raise RunnerException(
    #         *get_error_by_code(error_code, runner_error_codes, logger)
    #     )

    total_number_of_files = len(file_metadata_df)
    logger.info(f"total_number_of_files: {total_number_of_files}")

    memory_limit: str = "8"
    submission_module_name: str = "submission.submission_wrapper"
    submission_function_name: str = config_data["function_name"]
    data_dir: str = os.path.abspath(data_dir)
    results_dir: str = os.path.abspath(results_dir)

    volume_host_data_dir = os.environ.get("DOCKER_HOST_VOLUME_DATA_DIR")
    volume_host_results_dir = os.environ.get("DOCKER_HOST_VOLUME_RESULTS_DIR")

    if volume_host_data_dir is None:
        # TODO: add error code
        raise RunnerException(
            *get_error_by_code(500, runner_error_codes, logger)
        )

    if volume_host_results_dir is None:
        # TODO: add error code
        raise RunnerException(
            *get_error_by_code(500, runner_error_codes, logger)
        )

    func_arguments_list = prepare_function_args_for_parallel_processing(
        image_tag=image_tag,
        memory_limit=memory_limit,
        submission_file_name=submission_module_name,
        submission_function_name=submission_function_name,
        current_evaluation_dir=current_evaluation_dir,
        data_dir=data_dir,
        results_dir=results_dir,
        volume_data_dir=volume_host_data_dir,
        volume_results_dir=volume_host_results_dir,
    )

    # Loop through each file and generate predictions

    # print(func_arguments_list)

    # raise Exception("Finished Successfully")

    number_of_errors = loop_over_files_and_generate_results(
        func_arguments_list
    )
    logger.info(f"number_of_errors: {number_of_errors}")

    # raise Exception("Finished Successfully")

    results_list = loop_over_results_and_generate_metrics(
        data_dir=data_dir,
        results_dir=results_dir,
        current_evaluation_dir=current_evaluation_dir,
    )

    # raise Exception("Finished Successfully")

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

    module_name = "submission"

    public_metrics_dict["module"] = module_name
    # Get the mean and median run times
    public_metrics_dict["mean_run_time"] = results_df["run_time"].mean()
    public_metrics_dict["median_run_time"] = results_df["run_time"].median()
    public_metrics_dict["function_parameters"] = [
        "time_series",
        *config_data["allowable_kwargs"],
    ]
    public_metrics_dict["data_requirements"] = results_df[
        "data_requirements"
    ].iloc[0]

    metrics_dict: dict[str, str | float] = {}

    def m_mean(df: pd.DataFrame, column: str):
        return df[column].mean()

    def m_median(df: pd.DataFrame, column: str):
        return df[column].median()

    metric_operations_mapping = {
        "mean": m_mean,
        "median": m_median,
    }

    perfomance_metrics_mapping = [
        "mean_absolute_error",
        "absolute_error",
        "runtime",
    ]

    # Get the mean and median absolute errors
    # when combining the metric and name for the public metrics dictionary,
    # do not add anything to them. mean_mean_average_error and median_mean_average_error
    # are valid keys, anything else breaks our results processing
    for metric in performance_metrics:

        if metric not in perfomance_metrics_mapping:

            logger.error(
                f"metric {metric} not found in perfomance_metrics_mapping"
            )
            # TODO: add error code

            raise RunnerException(
                *get_error_by_code(500, runner_error_codes, logger)
            )

        metrics_operations: dict[str, dict[str, str]] = config_data.get(
            "metrics_operations", {}
        )

        if metric not in metrics_operations:
            # TODO: add error code
            logger.error(
                f"metric {metric} not found in metrics_operations within config.json"
            )
            raise RunnerException(
                *get_error_by_code(500, runner_error_codes, logger)
            )

        operations = metrics_operations[metric]

        for operation in operations:
            if operation not in metric_operations_mapping:
                # TODO: add error code
                logger.error(
                    f"operation {operation} not found in metric_operations_mapping"
                )
                raise RunnerException(
                    *get_error_by_code(500, runner_error_codes, logger)
                )

            operation_function = metric_operations_mapping[operation]

            for val in config_data["ground_truth_compare"]:

                if metric == "runtime":
                    key = "run_time"
                else:
                    key = f"{metric}_{val}"

                if key not in results_df.columns:

                    logger.error(f"key {key} not found in results_df columns")

                    # TODO: add error code
                    raise RunnerException(
                        *get_error_by_code(500, runner_error_codes, logger)
                    )

                metric_result = operation_function(results_df, key)

                metric_result_dict = {f"{operation}_{key}": metric_result}
                metrics_dict.update(metric_result_dict)

    public_metrics_dict["metrics"] = metrics_dict

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
    results_df_private_all = pd.merge(
        results_df, file_metadata_df, on="file_name"
    )

    private_results_columns: list[str] = config_data["private_results_columns"]

    # Filter to only the necessary columns (available via the config)

    results_df_private = results_df_private_all[
        [
            col
            for col in private_results_columns
            if col in results_df_private_all.columns
        ]
    ]

    results_file_name = module_name + "_full_results.csv"

    private_results_file_name = "private_results.html"

    results_df_private.to_csv(os.path.join(results_dir, results_file_name))

    try:
        logger.info(f"Generating private report for submission...")

        generate_private_report_for_submission(
            results_df_private,
            "export",
            os.path.join(current_evaluation_dir, "template.py"),
            os.path.join(results_dir, private_results_file_name),
            logger,
        )

        logger.info("Private report generated successfully.")
    except Exception as e:
        logger.error("Error generating private report for submission.")
        logger.exception(e)

    # Loop through all of the plot dictionaries and generate plots and
    # associated tables for reporting
    # for plot in config_data["plots"]:
    #     if plot["type"] == "histogram":
    #         if "color_code" in plot:
    #             color_code = plot["color_code"]
    #         else:
    #             color_code = None
    #         gen_plot = generate_histogram(
    #             results_df_private, plot["x_val"], plot["title"], color_code
    #         )
    #         # Save the plot
    #         gen_plot.savefig(os.path.join(results_dir, plot["save_file_path"]))
    #         plt.close()
    #         plt.clf()
    #         # Write the stratified results to a table for private reporting
    #         # (if color_code param is not None)
    #         if color_code:
    #             stratified_results_tbl = pd.DataFrame(
    #                 results_df_private.groupby(color_code)[
    #                     plot["x_val"]
    #                 ].mean()
    #             )
    #             stratified_results_tbl.to_csv(
    #                 os.path.join(
    #                     results_dir,
    #                     module_name
    #                     + "_"
    #                     + str(color_code)
    #                     + "_"
    #                     + plot["x_val"]
    #                     + ".csv",
    #                 )
    #             )
    #     if plot["type"] == "scatter_plot":
    #         gen_plot = generate_scatter_plot(
    #             results_df_private, plot["x_val"], plot["y_val"], plot["title"]
    #         )
    #         # Save the plot
    #         gen_plot.savefig(os.path.join(results_dir, plot["save_file_path"]))
    #         plt.close()
    #         plt.clf()

    logger.info(f"number_of_errors: {number_of_errors}")

    success_rate = (
        (total_number_of_files - number_of_errors) / total_number_of_files
    ) * 100
    logger.info(f"success_rate: {success_rate}%")
    logger.info(
        f"{total_number_of_files - number_of_errors} out of {total_number_of_files} files processed successfully"
    )

    # public_metrics_dict["success_rate"] = success_rate
    return public_metrics_dict


def install_module_dependencies(
    s3_submission_zip_file_path,
    update_submission_status,
    submission_id,
    tmp_dir,
):
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
        update_submission_status(submission_id, FAILED)
        error_code = 2
        raise RunnerException(
            *get_error_by_code(error_code, runner_error_codes, logger)
        )

    return target_module_path, new_dir, submission_file_name, module_name


def create_function_args_for_file(
    file_metadata_row: pd.Series,
    system_metadata_row: pd.Series,
    allowable_kwargs: list[str],
):

    submission_file_name: str = cast(str, file_metadata_row["file_name"])

    # Join both the file and system metadata into a single dictionary
    merged_row = pd.merge(
        file_metadata_row.to_frame().T,
        system_metadata_row.to_frame().T,
        on="system_id",
        how="inner",
    ).squeeze()

    args: list[str] = []

    for argument in allowable_kwargs:
        if argument not in merged_row:
            logger.error(f"argument {argument} not found in merged_row")
            # raise RunnerException(
            #     *get_error_by_code(500, runner_error_codes, logger)
            # )
            args.append("")
            continue
        value = merged_row[argument]

        args.append(str(value))

    # Submission Args for the function
    function_args = (submission_file_name, *args)

    logger.info(f"function_args: {function_args}")

    return function_args


T = TypeVar("T")


def append_to_list(item: T, array: list[T] | None = None):
    if array is None:
        array = []
    array.append(item)
    return array


def prepare_function_args_for_parallel_processing(
    image_tag: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    current_evaluation_dir: str,
    data_dir: str,
    results_dir: str,
    volume_data_dir: str,
    volume_results_dir: str,
):

    file_metadata_df = pd.read_csv(
        os.path.join(data_dir, "metadata", "file_metadata.csv")
    )

    system_metadata_df = pd.read_csv(
        os.path.join(data_dir, "metadata", "system_metadata.csv")
    )

    config_data: dict[str, Any] = json.load(
        open(os.path.join(current_evaluation_dir, "config.json"))
    )

    function_args_list = None

    allowable_kwargs: list[str] = config_data.get("allowable_kwargs", {})

    logger.info(f"allowable_kwargs: {allowable_kwargs}")

    for file_number, (_, file_metadata_row) in enumerate(
        file_metadata_df.iterrows()
    ):

        system_metadata_row: pd.Series = system_metadata_df[
            system_metadata_df["system_id"] == file_metadata_row["system_id"]
        ].iloc[0]

        if system_metadata_row.empty:
            logger.error(
                f"system_metadata not found for system_id: {file_metadata_row['system_id']}"
            )
            raise RunnerException(
                *get_error_by_code(500, runner_error_codes, logger)
            )

        submission_args = create_function_args_for_file(
            file_metadata_row,
            system_metadata_row,
            allowable_kwargs,
        )

        logger.info(f"submission_args: {submission_args}")

        function_args = (
            image_tag,
            memory_limit,
            submission_file_name,
            submission_function_name,
            submission_args,
            volume_data_dir,
            volume_results_dir,
            logger,
        )

        function_args_list = append_to_list(function_args, function_args_list)

    if function_args_list is None:
        # TODO: add error code
        raise RunnerException(
            *get_error_by_code(500, runner_error_codes, logger)
        )

    return function_args_list


def run_submission(
    file_name: str,
    data_dir: str,
    associated_metadata: dict[str, Any],
    config_data: dict[str, Any],
    submission_function: Callable[P, pd.Series],
    function_parameters: list[str],
    row: pd.Series,
):
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
        submission_function, time_series, kwargs
    )

    return (
        data_outputs,
        function_run_time,
    )


def loop_over_files_and_generate_results(
    func_arguments_list: list[Tuple],
) -> int:

    # func_arguments_list = prepare_function_args_for_parallel_processing(
    #     file_metadata_df,
    #     system_metadata_df,
    #     data_dir,
    #     config_data,
    #     submission_function,
    #     function_parameters,
    #     function_name,
    #     performance_metrics,
    # )

    NUM_FILES_TO_TEST = 3

    test_func_argument_list, rest_func_argument_list = (
        func_arguments_list[:NUM_FILES_TO_TEST],
        func_arguments_list[NUM_FILES_TO_TEST:],
    )

    results: list[dict[str, Any]] = []
    number_of_errors = 0

    # Test the first two files
    logger.info(f"Testing the first {NUM_FILES_TO_TEST} files...")
    test_errors = dask_multiprocess(
        submission_task,
        test_func_argument_list,
        n_workers=NUM_FILES_TO_TEST,
        threads_per_worker=1,
        # memory_limit="16GiB",
        logger=logger,
    )

    errors = [error for error, error_code in test_errors]
    number_of_errors += sum(errors)

    if number_of_errors == NUM_FILES_TO_TEST:
        logger.error(
            f"Too many errors ({number_of_errors}) occurred in the first {NUM_FILES_TO_TEST} files. Exiting."
        )
        error_code = 7
        raise RunnerException(
            *get_error_by_code(error_code, runner_error_codes, logger)
        )

    # Test the rest of the files

    logger.info(f"Testing the rest of the files...")
    rest_errors = []
    try:
        rest_errors = dask_multiprocess(
            submission_task,
            rest_func_argument_list,
            # n_workers=4,
            threads_per_worker=1,
            # memory_limit="16GiB",
            logger=logger,
        )
    except SubmissionException as e:
        logger.error(f"Submission error: {e}")
        raise e
    except RunnerException as e:
        logger.error(f"Runner error: {e}")
        raise e
    except Exception as e:
        if e.args:
            if len(e.args) == 2:
                logger.error(f"Submission error: {e}")

                raise RunnerException(*e.args)
        logger.error(f"Submission error: {e}")
        raise RunnerException(
            *get_error_by_code(500, runner_error_codes, logger)
        )
    errors = [error for error, error_code in rest_errors]
    number_of_errors += sum(errors)

    # test_errors = [result for result, _ in test_errors if result is not None]
    # rest_errors = [result for result, _ in rest_errors if result is not None]

    # results.extend(test_errors)
    # results.extend(rest_errors)

    return number_of_errors


def loop_over_results_and_generate_metrics(
    data_dir: str,
    results_dir: str,
    current_evaluation_dir: str,
) -> list[dict[str, Any]]:
    all_results: list[dict[str, Any]] = []

    file_metadata_df: pd.DataFrame = pd.read_csv(
        os.path.join(data_dir, "metadata", "file_metadata.csv")
    )

    system_metadata_df = pd.read_csv(
        os.path.join(data_dir, "metadata", "system_metadata.csv")
    )

    config_data: dict[str, Any] = json.load(
        open(os.path.join(current_evaluation_dir, "config.json"))
    )

    submission_execution_times_df = pd.read_csv(
        os.path.join(results_dir, "execution_time.csv")
    )

    for _, file_metadata_row in file_metadata_df.iterrows():

        file_name = file_metadata_row["file_name"]

        system_metadata_dict: dict[str, Any] = dict(
            system_metadata_df[
                system_metadata_df["system_id"]
                == file_metadata_row["system_id"]
            ].iloc[0]
        )

        try:
            submission_runtime: float = cast(
                float,
                submission_execution_times_df[
                    submission_execution_times_df["file_name"] == file_name
                ]["execution_time"].iloc[0],
            )
        except IndexError:
            logger.error(
                f"submission_runtime not found for file {file_name}. Exiting."
            )
            continue

        function_parameters = ["time_series", *config_data["allowable_kwargs"]]

        result = generate_performance_metrics_for_submission(
            file_name,
            config_data,
            system_metadata_dict,
            results_dir,
            data_dir,
            submission_runtime,
            function_parameters,
        )

        logger.info(f"{file_name}: {result}")
        all_results.append(result)

    return all_results


def generate_performance_metrics_for_submission(
    file_name: str,
    config_data: dict[str, Any],
    system_metadata_dict: dict[str, Any],
    results_dir: str,
    data_dir: str,
    submission_runtime: float,
    function_parameters: list[str],
):

    performance_metrics = config_data["performance_metrics"]

    submission_output_row: pd.Series | None = None
    submission_output_series: pd.Series | None = None

    # Get the ground truth scalars that we will compare to
    ground_truth_dict: dict[str, Any] = dict()
    if config_data["comparison_type"] == "scalar":
        submission_output_row = cast(
            pd.Series,
            pd.read_csv(
                os.path.join(results_dir, file_name),
                index_col=0,
            ).iloc[0],
        )
        for val in config_data["ground_truth_compare"]:
            ground_truth_dict[val] = system_metadata_dict[val]
            logger.info(
                f'ground_truth_dict["{val}"]: {ground_truth_dict[val]}'
            )
    if config_data["comparison_type"] == "time_series":
        submission_output_series = cast(
            pd.Series,
            pd.read_csv(
                os.path.join(results_dir, file_name),
                index_col=0,
            ).squeeze(),
        )
        ground_truth_series: pd.Series = pd.read_csv(
            os.path.join(data_dir + "/validation_data/", file_name),
            index_col=0,
            parse_dates=True,
        ).squeeze()
        ground_truth_dict["time_series"] = ground_truth_series

        ground_truth_file_length = len(ground_truth_series)

        file_submission_result_length = len(submission_output_series)
        if file_submission_result_length != ground_truth_file_length:
            logger.error(
                f"{file_name} submission result length {file_submission_result_length} does not match ground truth file length {ground_truth_file_length}"
            )
            error_code = 8

            raise RunnerException(
                *get_error_by_code(error_code, runner_error_codes, logger)
            )

    # Convert the data outputs to a dictionary identical to the
    # ground truth dictionary
    output_dictionary: dict[str, Any] = dict()
    if config_data["comparison_type"] == "scalar":
        if submission_output_row is None:
            logger.error(
                f"submission_output_row is None for {file_name}. Exiting."
            )
            error_code = 9
            raise RunnerException(
                *get_error_by_code(error_code, runner_error_codes, logger)
            )

        for idx in range(len(config_data["ground_truth_compare"])):

            logger.info(f"submission_output_row: {submission_output_row}")
            logger.info(
                f"submission_output_row[{idx}]: {submission_output_row.iloc[idx]}"
            )
            logger.info(
                f"config_data['ground_truth_compare'][{idx}]: {config_data['ground_truth_compare'][idx]}"
            )

            output_dictionary[config_data["ground_truth_compare"][idx]] = (
                submission_output_row[idx]
            )
    if config_data["comparison_type"] == "time_series":
        output_dictionary["time_series"] = submission_output_series
    # Run routine for all of the performance metrics and append
    # results to the dictionary
    results_dictionary: dict[str, Any] = dict()
    results_dictionary["file_name"] = file_name

    # Set the data requirements in the dictionary, must be a list for DB array field
    results_dictionary["data_requirements"] = function_parameters
    # Loop through the rest of the performance metrics and calculate them
    # (this predominantly applies to error metrics)

    def p_absolute_error(output: pd.Series, ground_truth: pd.Series):
        difference = output - ground_truth
        absolute_difference = np.abs(difference)
        return absolute_difference

    def p_mean_absolute_error(output: pd.Series, ground_truth: pd.Series):
        output.index = ground_truth.index
        difference = output - ground_truth
        mean_absolute_error = np.mean(difference)
        return mean_absolute_error

    performance_metrics_map = {
        "absolute_error": p_absolute_error,
        "mean_absolute_error": p_mean_absolute_error,
    }

    for metric in performance_metrics:

        if metric == "runtime":
            # Set the runtime in the results dictionary
            results_dictionary["runtime"] = submission_runtime
            continue

        if metric not in performance_metrics_map:
            logger.error(
                f"performance metric {metric} not found in performance_metrics_map, Unhandled metric"
            )
            # TODO: add error code

            raise RunnerException(
                *get_error_by_code(500, runner_error_codes, logger)
            )

        performance_metric_function = performance_metrics_map[metric]

        for val in config_data["ground_truth_compare"]:

            results_dictionary[metric + "_" + val] = (
                performance_metric_function(
                    output_dictionary[val], ground_truth_dict[val]
                )
            )

    return results_dictionary


# @timeout(SUBMISSION_TIMEOUT)
# def run_submission_and_generate_performance_metrics(
#     file_name: str,
#     data_dir: str,
#     associated_system_metadata: dict[str, Any],
#     config_data: dict[str, Any],
#     submission_function: Callable[P, pd.Series],
#     function_parameters: list[str],
#     file_metadata_row: pd.Series,
#     function_name: str,
#     performance_metrics: list[str],
#     file_number: int,
# ):

#     error = False
#     try:
#         logger.info(f"{file_number} - running submission for file {file_name}")
#         # Get file_name, which will be pulled from database or S3 for
#         # each analysis
#         (
#             data_outputs,
#             function_run_time,
#         ) = run_submission(
#             file_name,
#             data_dir,
#             associated_system_metadata,
#             config_data,
#             submission_function,
#             function_parameters,
#             file_metadata_row,
#         )

#         results_dictionary = generate_performance_metrics_for_submission(
#             data_outputs,
#             function_run_time,
#             file_name,
#             data_dir,
#             associated_system_metadata,
#             config_data,
#             function_parameters,
#             performance_metrics,
#         )

#         return results_dictionary, error
#     except Exception as e:
#         logger.error(f"error running function {function_name}: {e}")
#         error = True
#         return None, error


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
