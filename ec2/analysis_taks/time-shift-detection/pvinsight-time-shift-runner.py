"""
Runner script for assessing the time shift validation algorithm. In this
script, the following occurs:
    1. Pull down all of the metadata associated with the data sets
    2. Loop through all metadata cases, pull down the associated data, and
    run the associated submission on it
    3. Aggregate the results for the entire data set and generate assessment 
    metrics. Assessment metrics will vary based on the type of analysis being
    run. For this analysis, the following is calculated:
        1. Mean Absolute Error between predicted time shift series and ground
        truth time series (in minutes)
        2. Average run time for each data set (in seconds)
    4. Further aggregate performance metrics into visualizations:
        -Distribution Histograms
        -Scatter plots
      This section will be dependent on the type of analysis being run.
"""

import pandas as pd
import ast
import os
from importlib import import_module
import inspect
import time
from collections import ChainMap
import seaborn as sns
import matplotlib.pyplot as plt
import json
import numpy as np

from utilities import progress

MODULE_NAME = "pvanalytics-cpd-module-pva"


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


if __name__ == "__main__":
    # Read in the JSON associated with the run
    with open("config.json") as f:
        config_data = json.load(f)
    # Load in the module that we're going to test on.
    module_to_import = MODULE_NAME
    # Generate list for us to store all of our results for the module
    results_list = list()
    # Load in data set that we're going to analyze.
    # System metadata: This CSV represents the system_metadata table, which is
    # a master table for associated system metadata (system_id, name, azimuth,
    # tilt, etc.)
    system_metadata = pd.read_csv("./data/system_metadata.csv")
    # File metadata: This file represents the file_metadata table, which is
    # the master table for files associated with different tests (az-tilt,
    # time shifts, degradation, etc.). Contains file name, associated file
    # information (sampling frequency, specific test, timezone, etc) as well
    # as ground truth information to test against in the validation_dictionary
    # field
    file_metadata = pd.read_csv("./data/file_metadata.csv")
    # Validation tests: This file represents the validation_tests table,
    # which is the master table associated with each of the tests run on the
    # PVInsight Validation Hub. This table contains information on test type
    # (example: time_shifts, az_tilt_detection, etc), as well as function name
    # for each test type, performance metrics outputs (how to assess
    # test performance), as well as expected function outputs and function
    # output types (in order). This provides a standardized template of
    # what to expect (input, output, naming conventions) for each test
    validation_tests = pd.read_csv("./data/validation_tests.csv")
    # File category link: This file represents the file_category_link table,
    # which links specific files in the file_metadata table to categories in
    # the validation_tests table. This table exists specifically to allow for
    # many-to-many relationships, where one file can link to multiple
    # categories/tests, and multiple categories/tests can link to multiple
    # files. This table exists solely to link these two tables together
    # when performing testing.
    file_category_link = pd.read_csv("./data/file_test_link.csv")
    # Link the above tables together to get all of the files associated
    # with the time_shift category in the validation_tests table.
    time_shift_test_information = dict(
        validation_tests[
            validation_tests["category_name"] == config_data["category_name"]
        ].iloc[0]
    )
    # Get the associated metrics we're supposed to calculate
    performance_metrics = ast.literal_eval(
        time_shift_test_information["performance_metrics"]
    )
    # Get all of the linked files for time shift analysis via a series
    # of dataframe joins
    associated_file_ids = list(
        file_category_link[
            file_category_link["category_id"]
            == time_shift_test_information["category_id"]
        ]["file_id"]
    )
    associated_files = file_metadata[
        file_metadata["file_id"].isin(associated_file_ids)
    ]
    associated_files = associated_files
    # Get the information associated with the module to run the tests
    # Get the name of the function we want to import associated with this
    # test
    function_name = time_shift_test_information["function_name"]
    # Import designated module via importlib
    module = import_module(module_to_import)
    function = getattr(module, function_name)
    function_parameters = list(inspect.signature(function).parameters)
    # Loop through each file and generate predictions
    total = len(associated_files)
    t_start = time.time()
    for index, row in associated_files.iterrows():
        progress(
            index,
            total,
            status=f"elapsed time: {(time.time() - t_start) / 60:.2f} minutes",
        )
        # Get file_name, which will be pulled from database or S3 for
        # each analysis
        file_name = row["file_name"]
        # Get associated system ID
        system_id = row["system_id"]
        # Get all of the associated metadata for the particular file based
        # on its system ID. This metadata will be passed in via kwargs for
        # any necessary arguments
        associated_metadata = dict(
            system_metadata[system_metadata["system_id"] == system_id].iloc[0]
        )
        # Get the ground truth scalars that we will compare to
        ground_truth_dict = dict()
        if config_data["comparison_type"] == "scalar":
            for val in config_data["ground_truth_compare"]:
                ground_truth_dict[val] = associated_metadata[val]
        if config_data["comparison_type"] == "time_series":
            ground_truth_series = pd.read_csv(
                os.path.join("./data/validation_data/", file_name),
                index_col=0,
                parse_dates=True,
            ).squeeze()
            ground_truth_dict["time_series"] = ground_truth_series
        # Create master dictionary of all possible function kwargs
        kwargs_dict = dict(ChainMap(dict(row), associated_metadata))
        # Filter out to only allowable args for the function
        kwargs_dict = {
            key: kwargs_dict[key] for key in config_data["allowable_kwargs"]
        }
        # Now that we've collected all of the information associated with the
        # test, let's read in the file as a pandas dataframe (this data
        # would most likely be stored in an S3 bucket)
        time_series = pd.read_csv(
            os.path.join("./data/file_data/", file_name),
            index_col=0,
            parse_dates=True,
        ).squeeze()
        time_series = time_series.asfreq(
            str(row["data_sampling_frequency"]) + "T"
        )
        # Filter the kwargs dictionary based on required function params
        kwargs = dict(
            (k, kwargs_dict[k])
            for k in function_parameters
            if k in kwargs_dict
        )
        # Get the performance metrics that we want to quantify
        performance_metrics = config_data["performance_metrics"]
        # Run the routine (timed)
        start_time = time.time()
        data_outputs = function(time_series, **kwargs).tz_localize(None)
        end_time = time.time()
        function_run_time = end_time - start_time
        # Convert the data outputs to a dictionary identical to the
        # ground truth dictionary
        output_dictionary = dict()
        if config_data["comparison_type"] == "scalar":
            for idx in range(len(config_data["ground_truth_compare"])):
                output_dictionary[config_data["ground_truth_compare"][idx]] = (
                    data_outputs[idx]
                )
        if config_data["comparison_type"] == "time_series":
            output_dictionary["time_series"] = data_outputs
        # Run routine for all of the performance metrics and append
        # results to the dictionary
        results_dictionary = dict()
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
                    error = np.abs(
                        output_dictionary[val] - ground_truth_dict[val]
                    )
                    results_dictionary[metric + "_" + val] = error
            elif metric == "mean_absolute_error":
                for val in config_data["ground_truth_compare"]:
                    error = np.mean(
                        np.abs(output_dictionary[val] - ground_truth_dict[val])
                    )
                    results_dictionary[metric + "_" + val] = error
        results_list.append(results_dictionary)
    progress(
        total,
        total,
        status=f"elapsed time: {(time.time() - t_start) / 60:.2f} minutes",
    )
    # Convert the results to a pandas dataframe and perform all of the
    # post-processing in the script
    results_df = pd.DataFrame(results_list)
    # Build out the final processed results:
    #   1) Public reporting: mean MAE, mean run time, etc.
    #   2) Private reporting: graphics and tables split by different factors
    # First get mean value for all the performance metrics and save (this will
    # be saved to a public metrics dictionary)
    public_metrics_dict = dict()
    public_metrics_dict["module"] = module_to_import
    # Get the mean and median run times
    public_metrics_dict["mean_run_time"] = results_df["run_time"].mean()
    public_metrics_dict["median_run_time"] = results_df["run_time"].median()
    public_metrics_dict["function_parameters"] = function_parameters
    for metric in performance_metrics:
        if "absolute_error" in metric:
            for val in config_data["ground_truth_compare"]:
                public_metrics_dict["mean_" + metric + "_" + val] = results_df[
                    metric + "_" + val
                ].mean()
                public_metrics_dict["median_" + metric + "_" + val] = (
                    results_df[metric + "_" + val].median()
                )
    # TODO: Write public metric information to a public results table. here we
    # just write a json to illustrate that final outputs.
    with open(config_data["public_results_table"], "w") as fp:
        json.dump(public_metrics_dict, fp)
    # Now generate private results. These will be more specific to the
    # type of analysis being run as results will be color-coded by certain
    # parameters. These params will be available as columns in the
    # 'associated_files' dataframe
    results_df_private = pd.merge(results_df, associated_files, on="file_name")
    # Filter to only the necessary columns (available via the config)
    results_df_private = results_df_private[
        config_data["private_results_columns"]
    ]
    results_df_private.to_csv(
        os.path.join("./results", module_to_import + "_full_results.csv")
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
            gen_plot.savefig(plot["save_file_path"])
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
                        "./results",
                        module_to_import
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
            gen_plot.savefig(plot["save_file_path"])
            plt.close()
            plt.clf()
