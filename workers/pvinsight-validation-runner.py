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

import pandas as pd
import ast
import os
from importlib import import_module
import inspect
import time
from collections import ChainMap
from sklearn.metrics import mean_absolute_error
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

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger
logger = logging.getLogger(__name__)

def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return 'PROD' not in os.environ

is_s3_emulation = is_local()

if is_s3_emulation:
    api_base_url = 'api:8005'
else:
    api_base_url = 'api.pv-validation-hub.org'

S3_BUCKET_NAME = "pv-validation-hub-bucket"

def pull_from_s3(s3_file_path):
    logger.info(f"pulling file {s3_file_path} from s3")
    if s3_file_path.startswith('/'):
        s3_file_path = s3_file_path[1:]
        logger.info(f"modified path to {s3_file_path}")

    if is_s3_emulation:
        s3_file_full_path = 'http://s3:5000/get_object/' + S3_BUCKET_NAME + "/" + s3_file_path
    else:
        s3_file_full_path = 's3://' + s3_file_path
    
    target_file_path = os.path.join('/tmp/', s3_file_full_path.split('/')[-1])

    if is_s3_emulation:
        r = requests.get(s3_file_full_path, stream=True)
        if r.status_code != 200:
            print(f"error get file {s3_file_path} from s3, status code {r.status_code} {r.content}", file=sys.stderr)
        with open(target_file_path, "wb") as f:
            f.write(r.content)
    else:
        s3 = boto3.client('s3')
        s3.download_file(S3_BUCKET_NAME, s3_file_path, target_file_path)

    return target_file_path


def push_to_s3(local_file_path, s3_file_path):
    if s3_file_path.startswith('/'):
        s3_file_path = s3_file_path[1:]

    if is_s3_emulation:
        s3_file_full_path = 'http://s3:5000/put_object/' + S3_BUCKET_NAME + "/" + s3_file_path
    else:
        s3_file_full_path = 's3://' + s3_file_path
    
    if is_s3_emulation:
        with open(local_file_path, "rb") as f:
            file_content = f.read()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                print(f"error put file {s3_file_path} to s3, status code {r.status_code} {r.content}", file=sys.stderr)
    else:
        s3 = boto3.client('s3')
        s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_path)


def convert_compressed_file_path_to_directory(compressed_file_path):
    path_components = compressed_file_path.split('/')
    path_components[-1] = path_components[-1].split('.')[0]
    path_components = '/'.join(path_components)
    return path_components


def get_file_extension(path):
    return path.split('/')[-1].split('.')[-1]


def decompress_file(path):
    if (get_file_extension(path) == 'gz'):
        with tarfile.open(path, "r:gz") as tar:
            tar.extractall(convert_compressed_file_path_to_directory(path))
    else:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(convert_compressed_file_path_to_directory(path))
    return convert_compressed_file_path_to_directory(path)


def get_module_file_name(module_dir):
    for root, _, files in os.walk(module_dir, topdown=True):
        for name in files:
            if name.endswith('.py'):
                return name.split('/')[-1]


def get_module_name(module_dir):
    return get_module_file_name(module_dir)[:-3]


def generate_histogram(dataframe, x_axis, title, color_code = None,
                       number_bins = 30):
    """
    Generate a histogram for a distribution. Option to color code the
    histogram by the color_code column parameter.
    """
    sns.displot(dataframe,
                x=x_axis,
                hue=color_code,
                multiple="stack",
                bins=number_bins)
    plt.title(title)
    plt.tight_layout()
    return plt


def generate_scatter_plot(dataframe, x_axis, y_axis, title):
    """
    Generate a scatterplot between an x- and a y-variable.
    """
    sns.scatterplot(data=dataframe,
                    x=x_axis,
                    y=y_axis)
    plt.title(title)
    plt.tight_layout()
    return plt


def run(module_to_import_s3_path,
        current_evaluation_dir=None):
    # If a path is provided, set the directories to that path, otherwise use default
    if current_evaluation_dir is not None:
        results_dir = current_evaluation_dir + "/results" if not current_evaluation_dir.endswith('/') else current_evaluation_dir + "results"
        data_dir = current_evaluation_dir + "/data" if not current_evaluation_dir.endswith('/') else current_evaluation_dir + "data"
    else:
        results_dir = "./results"
        data_dir = "./data"

    if current_evaluation_dir is not None:
        sys.path.append(current_evaluation_dir)  # append current_evaluation_dir to sys.path

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Ensure results directory exists
    os.makedirs(data_dir, exist_ok=True)
        
    # Load in the module that we're going to test on.

    target_module_compressed_file_path = pull_from_s3(module_to_import_s3_path)
    
    target_module_path = decompress_file(target_module_compressed_file_path)

    # get current directory, i.e. directory of runner.py file
    new_dir = os.path.dirname(os.path.abspath(__file__))

    file_name = get_module_file_name(target_module_path)
    module_name = get_module_name(target_module_path)

    # install submission dependency
    try:
        subprocess.check_call(["python", "-m", "pip", "install", "-r", os.path.join(target_module_path, 'requirements.txt')])
        print("submission dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print("error installing submission dependencies:", e)
    shutil.move(os.path.join(target_module_path, file_name), os.path.join(new_dir, file_name))

    # Generate list for us to store all of our results for the module
    results_list = list()
    # Load in data set that we're going to analyze.

    # Make GET requests to the Django API to get the system metadata
    # http://api.pv-validation-hub.org/system_metadata/systemmetadata/
    smd_url = f'http://{api_base_url}/system_metadata/systemmetadata/'
    system_metadata_response = requests.get(smd_url)

    # Convert the responses to DataFrames

    # System metadata: This CSV represents the system_metadata table, which is
    # a master table for associated system metadata (system_id, name, azimuth,
    # tilt, etc.)
    system_metadata = pd.DataFrame(system_metadata_response.json())

    # File category link: This file represents the file_category_link table,
    # which links specific files in the file_metadata table.
    # This table exists specifically to allow for
    # many-to-many relationships, where one file can link to multiple
    # categories/tests, and multiple categories/tests can link to multiple
    # files.
    file_test_link = pd.read_csv(os.path.join(current_evaluation_dir,
                                              "file_test_link.csv"))

    # Get the unique file ids
    unique_file_ids = file_test_link['file_id'].unique()

    # File metadata: This file represents the file_metadata table, which is
    # the master table for files associated with different tests (az-tilt,
    # time shifts, degradation, etc.). Contains file name, associated file
    # information (sampling frequency, specific test, timezone, etc) as well
    # as ground truth information to test against in the validation_dictionary
    # field
    # For each unique file id, make a GET request to the Django API to get the corresponding file metadata
    file_metadata_list = []
    for file_id in unique_file_ids:
        fmd_url = f'http://{api_base_url}/file_metadata/filemetadata/{file_id}/'
        response = requests.get(fmd_url)
        file_metadata_list.append(response.json())

    # Convert the list of file metadata to a DataFrame
    file_metadata = pd.DataFrame(file_metadata_list)
    
    # Read in the configuration JSON for the particular run
    with open(os.path.join(current_evaluation_dir, "config.json")) as f:
        config_data = json.load(f)

    # Get the associated metrics we're supposed to calculate
    performance_metrics = config_data['performance_metrics']
    logger.info(f"performance_metrics: {performance_metrics}")

    # Get the name of the function we want to import associated with this
    # test
    function_name = config_data['function_name']
    # Import designated module via importlib
    module = import_module(module_name)
    function = getattr(module, function_name)
    function_parameters = list(inspect.signature(function).parameters)
    # Loop through each file and generate predictions
    for index, row in file_metadata.iterrows():
        # Get file_name, which will be pulled from database or S3 for
        # each analysis
        file_name = row['file_name']
        # Get associated system ID
        system_id = row['system_id']
        # Get all of the associated metadata for the particular file based
        # on its system ID. This metadata will be passed in via kwargs for
        # any necessary arguments
        associated_metadata = dict(system_metadata[
            system_metadata['system_id'] == system_id].iloc[0])
        # Get the ground truth scalars that we will compare to
        ground_truth_dict = dict()
        if config_data['comparison_type'] == 'scalar':
            for val in config_data['ground_truth_compare']:
                ground_truth_dict[val] = associated_metadata[val]
        if config_data['comparison_type'] == 'time_series':
            ground_truth_series = pd.read_csv(
                    os.path.join(data_dir + "/validation_data/", file_name),
                    index_col=0,
                    parse_dates=True).squeeze()
            ground_truth_dict["time_series"] = ground_truth_series
        # Create master dictionary of all possible function kwargs
        kwargs_dict = dict(ChainMap(dict(row), associated_metadata))
        # Filter out to only allowable args for the function
        kwargs_dict = {key:kwargs_dict[key] for key in
                       config_data['allowable_kwargs']}
        # Now that we've collected all of the information associated with the
        # test, let's read in the file as a pandas dataframe (this data
        # would most likely be stored in an S3 bucket)
        time_series = pd.read_csv(os.path.join(data_dir + "/file_data/", file_name),
                                index_col=0,
                                parse_dates=True).squeeze()
        time_series = time_series.asfreq(
            str(row['data_sampling_frequency']) + "T")
        # Filter the kwargs dictionary based on required function params
        kwargs = dict((k, kwargs_dict[k]) for k in function_parameters
                      if k in kwargs_dict)
        # Run the routine (timed)
        start_time = time.time()
        data_outputs = function(time_series, **kwargs)
        end_time = time.time()
        function_run_time = (end_time - start_time)
        # Convert the data outputs to a dictionary identical to the
        # ground truth dictionary
        output_dictionary = dict()
        if config_data['comparison_type'] == 'scalar':
            for idx in range(len(config_data['ground_truth_compare'])):
                output_dictionary[config_data['ground_truth_compare'
                                              ][idx]] = data_outputs[idx]
        if config_data['comparison_type'] == 'time_series':
            output_dictionary['time_series'] = data_outputs
        # Run routine for all of the performance metrics and append
        # results to the dictionary
        results_dictionary = dict()
        results_dictionary['file_name'] = file_name
        # Set the runtime in the results dictionary
        results_dictionary['run_time'] = function_run_time
        # Set the data requirements in the dictionary
        results_dictionary['data_requirements'] = function_parameters
        # Loop through the rest of the performance metrics and calculate them
        # (this predominantly applies to error metrics)
        for metric in performance_metrics:
            if metric == 'absolute_error':
                # Loop through the input and the output dictionaries,
                # and calculate the absolute error
                for val in config_data['ground_truth_compare']:
                    error = np.abs(output_dictionary[val] -
                                   ground_truth_dict[val])
                    results_dictionary[metric + "_" + val] = error
            elif metric == 'mean_absolute_error':
                for val in config_data['ground_truth_compare']:
                    error = np.mean(np.abs(output_dictionary[val] -
                                           ground_truth_dict[val]))
                    results_dictionary[metric + "_" + val] = error
        results_list.append(results_dictionary)
        logger.info(f"results_dictionary: {results_dictionary}")
    # Convert the results to a pandas dataframe and perform all of the
    # post-processing in the script
    results_df = pd.DataFrame(results_list)
    logger.info(f"results_df: {results_df}")
    # Build out the final processed results:
    #   1) Public reporting: mean MAE, mean run time, etc.
    #   2) Private reporting: graphics and tables split by different factors
    # First get mean value for all the performance metrics and save (this will
    # be saved to a public metrics dictionary)
    public_metrics_dict = dict()
    public_metrics_dict['module'] = module_name
    # Get the mean and median run times
    public_metrics_dict['mean_run_time'] = results_df['run_time'].mean()
    public_metrics_dict['median_run_time'] = results_df['run_time'].median()
    public_metrics_dict['function_parameters'] = function_parameters

    # Get the mean and median absolute errors
    # when combining the metric and name for the public metrics dictionary,
    # do not add anything to them. mean_mean_average_error and median_mean_average_error
    # are valid keys, anything else breaks our results processing
    for metric in performance_metrics:
        if 'absolute_error' in metric:
            for val in config_data['ground_truth_compare']:
                logger.info(f"metric: {metric}, val: {val}, combined: {'mean_' + metric}")
                public_metrics_dict['mean_' + metric] = \
                    results_df[metric + "_" + val].mean()
                public_metrics_dict['median_' + metric] = \
                    results_df[metric + "_" + val].median()   
    # Write public metric information to a public results table.
    with open(os.path.join(results_dir, config_data['public_results_table']),
              'w') as fp:
        json.dump(public_metrics_dict, fp)

    logger.info(f"public_metrics_dict: {public_metrics_dict}")
    # Now generate private results. These will be more specific to the
    # type of analysis being run as results will be color-coded by certain
    # parameters. These params will be available as columns in the
    # 'associated_files' dataframe
    results_df_private = pd.merge(results_df,
                                  file_metadata,
                                  on='file_name')
    # Filter to only the necessary columns (available via the config)
    results_df_private = results_df_private[config_data["private_results_columns"]]
    results_df_private.to_csv(
        os.path.join(results_dir,
                      module_name + "_full_results.csv"))
    # Loop through all of the plot dictionaries and generate plots and
    # associated tables for reporting
    for plot in config_data['plots']:
        if plot['type'] == 'histogram':
            if 'color_code' in plot:
                color_code = plot['color_code']
            else:
                color_code = None
            gen_plot = generate_histogram(results_df_private,
                                          plot['x_val'],
                                          plot['title'],
                                          color_code)
            # Save the plot
            gen_plot.savefig(os.path.join(results_dir,
                                          plot['save_file_path']))
            plt.close()
            plt.clf()
            # Write the stratified results to a table for private reporting
            # (if color_code param is not None)
            if color_code:
                stratified_results_tbl = pd.DataFrame(
                    results_df_private.groupby(color_code)[
                        plot['x_val']].mean())
                stratified_results_tbl.to_csv(
                    os.path.join(results_dir,
                                 module_name + '_' + str(color_code) + 
                                  '_' + plot['x_val'] + '.csv'))
        if plot['type'] == 'scatter_plot':
            gen_plot = generate_scatter_plot(results_df_private,
                                             plot['x_val'],
                                             plot['y_val'],
                                             plot['title'])
            # Save the plot
            gen_plot.savefig(os.path.join(results_dir,
                                          plot['save_file_path']))
            plt.close()
            plt.clf()
    return public_metrics_dict



if __name__ == '__main__':
    run('pv-validation-hub-bucket/submission_files/submission_user_1/submission_1/archive.tar.gz')
    push_to_s3('/pv-validation-hub-bucket/submission_files/submission_user_1/submission_1/results/time-shift-public-metrics.json', 'pv-validation-hub-bucket/test_bucket/test_subfolder/res.json')
