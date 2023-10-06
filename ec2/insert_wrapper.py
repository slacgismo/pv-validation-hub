from insert_analysis import InsertAnalysis
import pandas as pd
import os
import json
import requests

def get_input_or_default(prompt, default_value):
    """Query user for input, return default if none provided."""
    value = input(prompt + f" (Default: {default_value}): ")
    return value if value else default_value

# Load default paths from config.json
with open('routes.json', 'r') as file:
    config = json.load(file)

def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return 'AWS_EXECUTION_ENV' not in os.environ

is_s3_emulation = is_local()

BASE_API_URL = config['local']['api'] if is_s3_emulation else config['prod']['api']

# Fetch data from the remote API
def fetch_data_from_api(endpoint):
    response = requests.get(BASE_API_URL + endpoint)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        print(f"Error fetching data from {endpoint}. Status code: {response.status_code}")
        return pd.DataFrame()

# Fetching the data
db_metadata_df = fetch_data_from_api("system_metadata/systemmetadata/")
db_file_metadata_df = fetch_data_from_api("file_metadata/filemetadata/")

# Query user for paths or use defaults
config_file_path = get_input_or_default("Enter path for config_file", config['config_file_path'])
file_data_path = get_input_or_default("Enter path for file_data", config['file_data_path'])
sys_metadata_file_path = get_input_or_default("Enter path for sys_metadata_file", config['sys_metadata_file_path'])
file_metadata_file_path = get_input_or_default("Enter path for file_metadata_file", config['file_metadata_file_path'])
evaluation_scripts_path = get_input_or_default("Enter path for evaluation_scripts", config['evaluation_scripts_path'])

r = InsertAnalysis(db_metadata_df,
                   db_file_metadata_df,
                   config_file_path=config_file_path,
                   file_data_path=file_data_path,
                   sys_metadata_file_path=sys_metadata_file_path,
                   file_metadata_file_path=file_metadata_file_path)

sys_data_insert = r.buildSystemMetadata()
file_data_insert = r.buildFileMetadata(s3_path=config['local']['s3'] if is_s3_emulation else config['prod']['s3'])
s3_insert_list = r.buildS3fileInserts()

new_folder = r.insertConfig(evaluation_scripts_path)
r.generateFileTestLinker(new_folder)


db = ""
s3 = ""
puser = ""
ppass = ""

if (is_s3_emulation):
    db = route_data.local.db
    s3 = route_data.local.s3
    puser = route_data.local.puser
    ppass = route_data.local.ppass
