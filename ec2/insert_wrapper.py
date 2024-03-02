import pandas as pd
import os
import json
import requests

from insert_analysis import InsertAnalysis


def get_input_or_default(prompt, default_value):
    """Query user for input, return default if none provided."""
    value = input(prompt + f" (Default: {default_value}): ")
    return value if value else default_value


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return "AWS_EXECUTION_ENV" not in os.environ


# Fetch data from the remote API
def fetch_data_from_api(endpoint):
    response = requests.get(f"{api_url}{endpoint}")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        print(
            f"Error fetching data from {endpoint}. Status code: {response.status_code}"
        )
        return pd.DataFrame()


# Load default paths from routes.json
with open("routes.json", "r") as file:
    config = json.load(file)

is_s3_emulation = is_local()

s3_url = config["local"]["s3"] if is_s3_emulation else config["prod"]["s3"]

api_url = config["local"]["api"] if is_s3_emulation else config["prod"]["api"]

# Fetching the data
db_metadata_df = fetch_data_from_api("/system_metadata/systemmetadata/")
db_file_metadata_df = fetch_data_from_api("/file_metadata/filemetadata/")


# Query user for paths or use defaults
config_file_path = get_input_or_default(
    "Enter path for config_file", config["config_file_path"]
)
file_data_path = get_input_or_default(
    "Enter path for file_data", config["file_data_path"]
)
evaluation_scripts_path = get_input_or_default(
    "Enter path for evaluation_scripts", config["evaluation_scripts_path"]
)
validation_data_path = get_input_or_default(
    "Enter path for validation_data", config["validation_data_path"]
)
sys_metadata_file_path = get_input_or_default(
    "Enter path for sys_metadata_file", config["sys_metadata_file_path"]
)
file_metadata_file_path = get_input_or_default(
    "Enter path for file_metadata_file", config["file_metadata_file_path"]
)
validation_tests_file_path = get_input_or_default(
    "Enter path for validation_tests", config["validation_tests_file_path"]
)

print(
    f"db_metadata_df: {db_metadata_df}\n"
    f"db_file_metadata_df: {db_file_metadata_df}\n"
    f"config_file_path: {config_file_path}\n"
    f"file_data_path: {file_data_path}\n"
    f"sys_metadata_file_path: {sys_metadata_file_path}\n"
    f"file_metadata_file_path: {file_metadata_file_path}\n"
    f"evaluation_scripts_path: {evaluation_scripts_path}\n"
    f"validation_tests_file_path: {validation_tests_file_path}\n"
)

# exit()


r = InsertAnalysis(
    db_metadata_df,
    db_file_metadata_df,
    config_file_path=config_file_path,
    file_data_path=file_data_path,
    sys_metadata_file_path=sys_metadata_file_path,
    file_metadata_file_path=file_metadata_file_path,
    validation_tests_file_path=validation_tests_file_path,
    validation_data_path=validation_data_path,
    evaluation_scripts_path=evaluation_scripts_path,
)
r.insertData(api_url)
