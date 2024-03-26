import json

from insert_analysis import InsertAnalysis


def get_input_or_default(prompt, default_value):
    """Query user for input, return default if none provided."""
    value = input(prompt + f" (Default: {default_value}): ")
    return value if value else default_value


# def is_local():
#     """
#     Checks if the application is running locally or in an Amazon ECS environment.

#     Returns:
#         bool: True if the application is running locally, False otherwise.
#     """
#     return "AWS_EXECUTION_ENV" not in os.environ


if __name__ == "__main__":

    # Load default paths from routes.json
    with open("routes.json", "r") as file:

        config = json.load(file)

        is_local = True

        api_url = config["local"]["api"] if is_local else config["prod"]["api"]
        s3_url = config["local"]["s3"] if is_local else config["prod"]["s3"]

        config_file_path = config["config_file_path"]
        file_data_folder_path = config["file_data_folder_path"]
        evaluation_scripts_folder_path = config["evaluation_scripts_folder_path"]
        sys_metadata_file_path = config["sys_metadata_file_path"]
        file_metadata_file_path = config["file_metadata_file_path"]
        validation_data_folder_path = config["validation_data_folder_path"]

        print(f"api_url: {api_url}")
        print(f"s3_url: {s3_url}")
        print(f"config_file_path: {config_file_path}")
        print(f"file_data_folder_path: {file_data_folder_path}")
        print(f"evaluation_scripts_folder_path: {evaluation_scripts_folder_path}")
        print(f"sys_metadata_file_path: {sys_metadata_file_path}")
        print(f"file_metadata_file_path: {file_metadata_file_path}")
        print(f"validation_data_folder_path: {validation_data_folder_path}")

        # exit()

        r = InsertAnalysis(
            api_url=api_url,
            config_file_path=config_file_path,
            file_data_folder_path=file_data_folder_path,
            sys_metadata_file_path=sys_metadata_file_path,
            file_metadata_file_path=file_metadata_file_path,
            validation_data_folder_path=validation_data_folder_path,
            evaluation_scripts_folder_path=evaluation_scripts_folder_path,
            s3_bucket_name="pv-validation-hub-bucket",
            s3_url=s3_url,
            is_local=is_local,
        )
        r.insertData(api_url)
