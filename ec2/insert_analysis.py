"""
Class for building out the data for insertion into the Postgres database,
including system metadata and file metadata.
"""

import json
from logging import Logger
from typing import Any, cast
import numpy as np
import pandas as pd
import os
import shutil
import requests
import boto3
import sys
import requests

from utility import (
    request_to_API_w_credentials as request_to_API_w_auth,
    with_credentials,
)


def request_to_API_w_credentials(
    api_url: str,
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
    **kwargs,
) -> dict[str, Any]:
    request_wrapper = with_credentials(api_url)(request_to_API_w_auth)

    endpoint = f"{api_url}/{endpoint}"
    return request_wrapper(method, endpoint, data, headers, logger, **kwargs)


# Fetch data from the remote API
def get_data_from_api_to_df(api_url: str, endpoint: str) -> pd.DataFrame:

    data = request_to_API_w_credentials(api_url, "GET", endpoint=endpoint)

    # Check if the data is a dictionary of scalar values
    if isinstance(data, dict) and all(np.isscalar(v) for v in data.values()):
        # If it is, wrap the values in lists
        data = {k: [v] for k, v in data.items()}
    return pd.DataFrame(data)


def post_data_to_api_to_df(
    api_url: str, endpoint: str, data: dict[str, Any]
) -> pd.DataFrame:

    data = request_to_API_w_credentials(
        api_url, "POST", endpoint=endpoint, data=data
    )

    # Check if the data is a dictionary of scalar values
    if isinstance(data, dict) and all(np.isscalar(v) for v in data.values()):
        # If it is, wrap the values in lists
        data = {k: [v] for k, v in data.items()}
    return pd.DataFrame(data)


def hasAllColumns(df, cols: list):
    """
    Check if the dataframe has the required columns for overlap
    checking.
    """
    return all(col in df.columns for col in cols)


def upload_to_s3_bucket(
    s3_url: str,
    bucket_name: str,
    local_path: str,
    upload_path: str,
    is_local: bool,
):
    """
    Upload file to S3 bucket and return object URL

    Parameters
    ----------
    bucket_name: String. Name of the S3 bucket.
    local_path: String. Local path to the file we want to upload.
    upload_path: String. Path in the S3 bucket where we want to upload the file.

    Returns
    -------
    String: URL of the object in the S3 bucket.
    """

    if is_local:
        upload_path = os.path.join(bucket_name, upload_path)
        s3_file_full_path = f"{s3_url}/put_object/{upload_path}"
        with open(local_path, "rb") as f:
            file_content = f.read()

            print(s3_file_full_path, file_content[:100])
            # exit()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                print(
                    f"error put file {upload_path} to s3, status code {r.status_code} {r.content}",
                    file=sys.stderr,
                )
                return None
            else:
                return s3_file_full_path.replace(
                    f"{s3_url}/put_object/", f"{s3_url}/get_object/"
                )
    else:
        """Upload file to S3 bucket and return object URL"""
        s3 = boto3.client("s3")

        try:
            print(f"uploading {local_path} to {bucket_name}/{upload_path}")
            s3.upload_file(local_path, bucket_name, upload_path)
            print(f"uploaded {local_path} to {bucket_name}/{upload_path}")
        except Exception as e:
            print(
                f"error uploading {local_path} to {bucket_name}/{upload_path}"
            )
            raise e

        bucket_location = boto3.client("s3").get_bucket_location(
            Bucket=bucket_name
        )
        object_url = "https://{}.s3.{}.amazonaws.com/{}".format(
            bucket_name, bucket_location["LocationConstraint"], upload_path
        )
        print(
            f"uploaded {local_path} to {bucket_name}/{upload_path} returns {object_url}"
        )
        return object_url


def list_s3_bucket(
    is_s3_emulation: bool, s3_bucket_name: str, s3_dir: str
) -> list[str]:
    print(f"list s3 bucket {s3_dir}")
    if s3_dir.startswith("/"):
        s3_dir = s3_dir[1:]

    if is_s3_emulation:
        s3_dir_full_path = "http://s3:5000/list_bucket/" + s3_dir
        # s3_dir_full_path = 'http://localhost:5000/list_bucket/' + s3_dir
    else:
        s3_dir_full_path = "s3://" + s3_dir

    all_files: list[str] = []
    if is_s3_emulation:
        r = requests.get(s3_dir_full_path)
        ret = r.json()
        for entry in ret["Contents"]:
            all_files.append(os.path.join(s3_dir.split("/")[0], entry["Key"]))
    else:
        # check s3_dir string to see if it contains "pv-validation-hub-bucket/"
        # if so, remove it
        s3_dir = s3_dir.replace("pv-validation-hub-bucket/", "")
        print(f"dir after removing pv-validation-hub-bucket/ returns {s3_dir}")

        s3 = boto3.client("s3")
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=s3_bucket_name, Prefix=s3_dir)
        for page in pages:
            if page["KeyCount"] > 0:
                if "Contents" in page:
                    for entry in page["Contents"]:
                        if "Key" in entry:
                            all_files.append(entry["Key"])

        # remove the first entry if it is the same as s3_dir
        if len(all_files) > 0 and all_files[0] == s3_dir:
            all_files.pop(0)

    print(f"listed s3 bucket {s3_dir_full_path} returns {all_files}")
    return all_files


class InsertAnalysis:

    def __init__(
        self,
        config_file_path: str,
        file_data_folder_path: str,
        validation_data_folder_path: str,
        evaluation_scripts_folder_path: str,
        sys_metadata_file_path: str,
        file_metadata_file_path: str,
        private_report_template_file_path: str,
        # validation_tests_file_path: str,
        s3_bucket_name: str,
        api_url: str,
        s3_url: str,
        is_local: bool,
    ):

        config: dict[str, Any] = json.load(open(config_file_path, "r"))
        self.config = config
        self.is_local = is_local

        self.api_url = api_url
        self.s3_url = s3_url

        # Fetching the data
        db_sys_metadata_df = get_data_from_api_to_df(
            self.api_url, "system_metadata/systemmetadata"
        )
        db_file_metadata_df = get_data_from_api_to_df(
            self.api_url, "file_metadata/filemetadata"
        )

        self.db_sys_metadata_df = db_sys_metadata_df
        self.db_file_metadata_df = db_file_metadata_df
        self.config_file_path = config_file_path
        self.private_report_template_file_path = (
            private_report_template_file_path
        )
        self.file_data_folder_path = file_data_folder_path
        self.evaluation_scripts_folder_path = evaluation_scripts_folder_path
        # self.validation_tests_file_path = validation_tests_file_path
        self.new_sys_metadata_df: pd.DataFrame = pd.read_csv(
            sys_metadata_file_path
        )
        self.new_file_metadata_df: pd.DataFrame = pd.read_csv(
            file_metadata_file_path
        )

        self.analysis_id = None
        self.system_id_mapping = dict()
        self.file_id_mapping = dict()
        self.s3_bucket_name = s3_bucket_name
        self.validation_data_folder_path = validation_data_folder_path

        self.hasAllValidNewAnalysisData()

    def hasAllValidNewAnalysisData(self):
        """
        Check if we have all the required data to create a new analysis.

        Returns
        -------
        bool: True if we have all the required data, False otherwise.
        """
        file_metadata_files = self.new_file_metadata_df["file_name"]

        # are there any duplicates?
        if file_metadata_files.duplicated().any():
            raise ValueError(
                "There are duplicate file names in the file metadata."
            )

        sys_metadata_files = self.new_sys_metadata_df["name"]

        # are there any duplicates?
        if sys_metadata_files.duplicated().any():
            raise ValueError(
                "There are duplicate system names in the system metadata."
            )

        file_data_files = os.listdir(self.file_data_folder_path)

        if not all(file in file_data_files for file in file_metadata_files):
            raise ValueError(
                "The file metadata contains files that are not in the file data folder."
            )

        validation_data_files = os.listdir(self.validation_data_folder_path)

        if not all(
            file in validation_data_files for file in file_metadata_files
        ):
            raise ValueError(
                "The file metadata contains files that are not in the validation data folder."
            )

        template_file_exists = os.path.exists(
            self.private_report_template_file_path
        )

        if not template_file_exists:
            raise ValueError(
                "The private report template file does not exist."
            )

        print("All files are in the right place.")

        return True

    def getAllAnalyses(self) -> pd.DataFrame:
        """
        Get all analyses from the API.



        Returns
        -------
        List: List of all analyses.
        """

        df = get_data_from_api_to_df(self.api_url, "analysis/home")

        return df

    # Create and upload to the API and S3
    def createAnalysis(
        self,
        db_analysis_df: pd.DataFrame,
        force: bool = False,
    ):
        """
        Create a new analysis in the API.
        """

        # check if the analysis already exists

        if (
            not db_analysis_df.empty
            and self.config["category_name"]
            in list(db_analysis_df["analysis_name"])
            and not force
        ):
            db_analysis_id = cast(
                int,
                db_analysis_df.loc[
                    db_analysis_df["analysis_name"]
                    == self.config["category_name"],
                    "analysis_id",
                ].values[  # type: ignore
                    0
                ],
            )
            print(
                f'Analysis {self.config["category_name"]} already exists with id {db_analysis_id}'
            )
            print(f"{db_analysis_id} is { type(db_analysis_id)}")
            self.analysis_id = db_analysis_id

        else:

            if force:
                print("Force is True. Creating a new analysis.")

            performance_metrics: list[str] | None = self.config.get(
                "performance_metrics", None
            )

            if not performance_metrics:
                raise ValueError(
                    "Performance metrics are required to create a new analysis."
                )

            display_errors: dict[str, str] = self.config.get(
                "display_metrics", {}
            )
            if not display_errors:
                raise ValueError(
                    "Display errors are required to create a new analysis. Add display_errors to the config file."
                )
            # for metric in performance_metrics:
            #     metric_words = metric.split("_")

            #     display_words = [word.capitalize() for word in metric_words]
            #     display = " ".join(display_words)

            #     display_error = (metric, display)
            #     display_errors.append(display_error)

            print("display_errors", display_errors)

            body = {
                "analysis_name": self.config["category_name"],
                "display_errors": display_errors,
                "total_files": len(self.new_file_metadata_df),
            }

            print("body", body)

            res = post_data_to_api_to_df(
                self.api_url, "analysis/create/", body
            )
            print("Analysis created")
            self.analysis_id = res["analysis_id"].values[0]

    def createSystemMetadata(self, sys_metadata_df: pd.DataFrame):
        """
        Upload the system metadata to the API.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        """

        body = sys_metadata_df.to_json(orient="records")
        systems_json_list = json.loads(body)

        for system in systems_json_list:

            json_body: dict[str, Any] = {}

            json_body["name"] = system["name"]
            json_body["azimuth"] = system["azimuth"]
            json_body["tilt"] = system["tilt"]
            json_body["elevation"] = system["elevation"]
            json_body["latitude"] = system["latitude"]
            json_body["longitude"] = system["longitude"]
            json_body["tracking"] = system["tracking"]
            if "dc_capacity" in system:
                print(system["dc_capacity"])
                if system["dc_capacity"] is not None:
                    json_body["dc_capacity"] = system["dc_capacity"]

            print(json_body)

            post_data_to_api_to_df(
                self.api_url, "/system_metadata/systemmetadata/", json_body
            )

    def createFileMetadata(self, file_metadata_df: pd.DataFrame):
        """
        Upload the file metadata and validation tests to the API and S3.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        """

        # s3_data_files = list_s3_bucket(self.is_local, self.s3_bucket_name, "data_files/analytical/")

        body = file_metadata_df.to_json(orient="records")
        metadata_json_list = json.loads(body)

        for metadata in metadata_json_list:

            json_body = {
                "system_id": metadata["system_id"],
                "file_name": metadata["file_name"],
                "timezone": metadata["timezone"],
                "data_sampling_frequency": metadata["data_sampling_frequency"],
                "issue": metadata["issue"],
                "subissue": metadata["subissue"],
            }

            print(json_body)

            post_data_to_api_to_df(
                self.api_url, "/file_metadata/filemetadata/", json_body
            )

            local_path = os.path.join(
                self.file_data_folder_path, metadata["file_name"]
            )
            upload_path = f'data_files/analytical/{metadata["file_name"]}'

            # upload metadata to s3
            upload_to_s3_bucket(
                self.s3_url,
                self.s3_bucket_name,
                local_path,
                upload_path,
                self.is_local,
            )

    def uploadValidationData(self):

        file_metadata_names = self.new_file_metadata_df["file_name"]

        for file_name in file_metadata_names:
            # upload validation data to s3
            local_path = os.path.join(
                self.validation_data_folder_path, file_name
            )
            upload_path = (
                f"data_files/ground_truth/{str(self.analysis_id)}/{file_name}"
            )
            upload_to_s3_bucket(
                self.s3_url,
                self.s3_bucket_name,
                local_path,
                upload_path,
                self.is_local,
            )

    def createEvaluationScripts(self):
        """
        Upload the evaluation scripts to the S3 bucket.
        """

        evaluation_folder_path = os.path.join(
            self.evaluation_scripts_folder_path, f"{str(self.analysis_id)}/"
        )

        # Upload the evaluation scripts to the S3 bucket
        for root, dirs, files in os.walk(evaluation_folder_path):
            directory = os.path.dirname(root)

            folder = "/".join(directory.split("/")[-2:])

            for file in files:

                local_path = os.path.join(evaluation_folder_path, file)
                upload_path = os.path.join(
                    folder,
                    file,
                )
                upload_to_s3_bucket(
                    self.s3_url,
                    self.s3_bucket_name,
                    local_path,
                    upload_path,
                    self.is_local,
                )

    def updateSystemMetadataIDs(self):
        """
        Update the system metadata IDs in the system metadata dataframe.

        Parameters
        ----------
        sys_metadata_df: Pandas dataframe. Dataframe of the system metadata.
        """

        db_sys_metadata_df = get_data_from_api_to_df(
            self.api_url, "system_metadata/systemmetadata"
        )

        self.db_sys_metadata_df = db_sys_metadata_df

        # Create a dictionary of the system metadata IDs
        db_system_name_to_id_mapping = dict(
            zip(
                db_sys_metadata_df["name"],
                db_sys_metadata_df["system_id"],
            )
        )

        counter = 0

        def map_system_id_to_db_system_id(self, ref_value, target_value):
            nonlocal counter
            new_system_id = db_system_name_to_id_mapping.get(ref_value)

            if not new_system_id:
                # new_system_id = max_system_id + counter
                # counter += 1
                raise ValueError("System ID not found")

            self.system_id_mapping[target_value] = int(new_system_id)
            return new_system_id

        df_new = self.new_sys_metadata_df.copy()

        # how do you create unique hash from columns from a dataframe?

        df_new["system_id"] = df_new.apply(
            lambda row: map_system_id_to_db_system_id(
                self,
                row["name"],
                row["system_id"],
            ),
            axis=1,
        )

        self.new_sys_metadata_df = df_new

    def updateFileMetadataIDs(self):
        """
        Update the file metadata IDs in the file metadata dataframe.

        Parameters
        ----------
        file_metadata_df: Pandas dataframe. Dataframe of the file metadata.
        """

        db_file_metadata_df = get_data_from_api_to_df(
            self.api_url, "file_metadata/filemetadata"
        )

        self.db_file_metadata_df = db_file_metadata_df

        # Create a dictionary of the file metadata IDs
        db_file_name_to_id_mapping: dict[str, int] = dict(
            zip(
                db_file_metadata_df["file_name"],
                db_file_metadata_df["file_id"],
            )
        )

        counter = 0

        def map_file_id_to_db_file_id(self, ref_value, target_value):
            nonlocal counter
            new_file_id = db_file_name_to_id_mapping.get(ref_value)

            if not new_file_id:
                # new_file_id = max_file_id + counter
                # counter += 1
                raise ValueError("File ID not found")

            self.file_id_mapping[target_value] = new_file_id
            return new_file_id

        df_new = self.new_file_metadata_df.copy()

        df_new["file_id"] = df_new.apply(
            lambda row: map_file_id_to_db_file_id(
                self, row["file_name"], row["file_id"]
            ),
            axis=1,
        )
        # self.db_file_metadata_df = df_new
        self.new_file_metadata_df = df_new

    def buildSystemMetadata(self):
        """
        Check for duplicates in the system metadata table. Build non duplicated
        system metadata for insert into the system_metadata table.
        """

        # Check cases to determine if we have overlap, using the name,
        # latitude, and longitude fields

        df_new = self.new_sys_metadata_df.copy()
        df_old = self.db_sys_metadata_df.copy()

        if not hasAllColumns(df_new, ["name", "latitude", "longitude"]):
            raise ValueError(
                "The new system metadata dataframe does not have the required columns. name, latitude, and longitude are required."
            )

        if not hasAllColumns(df_old, ["name", "latitude", "longitude"]):
            df_old = pd.DataFrame(
                [], columns=["name", "latitude", "longitude"]
            )

        same_systems = pd.merge(
            df_new, df_old, how="inner", on=["name", "latitude", "longitude"]
        )

        df_new = df_new[~df_new["name"].isin(list(same_systems["name"]))]

        system_metadata_columns = [
            "system_id",
            "name",
            "azimuth",
            "tilt",
            "elevation",
            "latitude",
            "longitude",
            "tracking",
            "dc_capacity",
        ]

        def addNAtoMissingColumns(df, columns):
            new_df = df.copy()
            for column in columns:
                if column not in df.columns:
                    new_df[column] = None
            return new_df

        # Return the system data ready for insertion
        df_modified = addNAtoMissingColumns(df_new, system_metadata_columns)
        print(df_modified.head(5))
        return df_modified

    def buildFileMetadata(self):
        """
        Check for duplicates in the file metadata table. Build non duplicated
        file metadata for insert into the file_metadata table.
        """

        overlapping_files = self.getOverlappingMetadataFiles()

        df_new = self.new_file_metadata_df.copy()

        # Remove the repeat systems from the metadata we want to insert
        df_new = df_new[
            ~df_new["file_name"].isin(list(overlapping_files["file_name"]))
        ]

        df_new["system_id"] = df_new["system_id"].map(self.system_id_mapping)

        # Check if any system IDs are missing
        if df_new["system_id"].isna().any():
            raise ValueError(
                "Some system IDs are missing from the system metadata dataframe."
            )

        # Fill in any missing values with "N/A"

        if "issue" not in df_new.columns:
            df_new["issue"] = "N/A"
        else:
            df_new["issue"] = df_new["issue"].fillna("N/A")

        if "subissue" not in df_new.columns:
            df_new["subissue"] = "N/A"
        else:
            df_new["subissue"] = df_new["subissue"].fillna("N/A")

        # self.new_file_metadata_df = df_new

        return df_new[
            [
                "system_id",
                "file_name",
                "timezone",
                "data_sampling_frequency",
                "issue",
                "subissue",
            ]
        ]

    # def buildValidationTests(self):
    #     """
    #     Build out the validation tests for insert into the validation_tests
    #     table.

    #     Returns
    #     -------
    #     Pandas dataframe: Pandas df ready for insert into the validation_tests
    #         table.
    #     """

    #     validation_tests_df = self.validation_tests_df[
    #         ["category_name", "performance_metrics", "function_name"]
    #     ]

    #     return validation_tests_df

    def getOverlappingMetadataFiles(self):
        """
        Return a dataframe files that are in both the new load and previously
        entered into the database.
        """
        df_new = self.new_file_metadata_df.copy()
        df_old = self.db_file_metadata_df.copy()

        if not hasAllColumns(df_new, ["file_name"]):
            raise ValueError(
                "The new file metadata dataframe does not have the required columns. file_name is required."
            )
        if not hasAllColumns(df_old, ["file_name"]):
            df_old = pd.DataFrame([], columns=["file_name", "file_id"])

        overlapping_files = pd.merge(
            df_new["file_name"],
            df_old[["file_name", "file_id"]],
            on=["file_name"],
        )
        return overlapping_files

    def prepareConfig(self):
        """
        Drop the config JSON into the new evaluation folder.
        """
        evaluation_folder_path = os.path.join(
            self.evaluation_scripts_folder_path, str(self.analysis_id)
        )
        if not os.path.exists(evaluation_folder_path):
            os.makedirs(evaluation_folder_path)
        # Drop the config JSON into the new folder

        shutil.copy(self.config_file_path, evaluation_folder_path)

        return evaluation_folder_path

    def prepareTemplate(self):
        evaluation_folder_path = os.path.join(
            self.evaluation_scripts_folder_path, str(self.analysis_id)
        )
        if not os.path.exists(evaluation_folder_path):
            os.makedirs(evaluation_folder_path)
        # Drop the config JSON into the new folder

        shutil.copy(
            self.private_report_template_file_path, evaluation_folder_path
        )

        return evaluation_folder_path

    def getSystemMetadataIDs(self):
        """
        Get the system metadata IDs from the API.



        Returns
        -------
        int: New system metadata ID.
        """

        endpoint = "system_metadata/systemmetadata"

        data = request_to_API_w_credentials(
            self.api_url, "GET", endpoint=endpoint
        )

        # r = requests.get(full_url)
        # if r.status_code != 200:
        #     raise ValueError(
        #         f"Error getting the system metadata from the API. Status code: {r.status_code}"
        #     )
        # data = r.json()
        new_system_id = len(data) + 1

        return new_system_id

    def prepareFileTestLinker(self):
        """
        Prepare the file test linker and drop it into the new evaluation folder.
        """

        file_test_link = self.new_file_metadata_df["file_id"]

        file_test_link.index.name = "test_id"

        local_file_path = os.path.join(
            self.evaluation_scripts_folder_path, str(self.analysis_id)
        )

        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path)

        # Write to the folder
        file_test_link_path = file_test_link.to_csv(
            os.path.join(local_file_path, "file_test_link.csv")
        )
        return file_test_link_path

    def insertData(self, force=False):
        """
        Insert all the data into the API and S3.
        """

        db_analyses_df = self.getAllAnalyses()
        self.createAnalysis(db_analyses_df, force)

        if not self.analysis_id:
            raise ValueError("Analysis ID not found or created.")

        # exit()
        new_sys_metadata_df = self.buildSystemMetadata()
        self.createSystemMetadata(new_sys_metadata_df)
        self.updateSystemMetadataIDs()

        new_file_metadata_df = self.buildFileMetadata()
        self.createFileMetadata(new_file_metadata_df)
        self.updateFileMetadataIDs()
        self.uploadValidationData()

        self.prepareFileTestLinker()
        self.prepareConfig()
        self.prepareTemplate()
        self.createEvaluationScripts()


if __name__ == "__main__":
    with open("routes.json", "r") as file:
        config = json.load(file)

        is_local = True

        api_url = config["local"]["api"] if is_local else config["prod"]["api"]
        s3_url = config["local"]["s3"] if is_local else config["prod"]["s3"]

        config_file_path = config["config_file_path"]
        file_data_folder_path = config["file_data_folder_path"]
        evaluation_scripts_folder_path = config[
            "evaluation_scripts_folder_path"
        ]
        sys_metadata_file_path = config["sys_metadata_file_path"]
        file_metadata_file_path = config["file_metadata_file_path"]
        validation_data_folder_path = config["validation_data_folder_path"]
        private_report_template_file_path = config[
            "private_report_template_file_path"
        ]

        r = InsertAnalysis(
            config_file_path=config_file_path,
            file_data_folder_path=file_data_folder_path,
            sys_metadata_file_path=sys_metadata_file_path,
            file_metadata_file_path=file_metadata_file_path,
            validation_data_folder_path=validation_data_folder_path,
            evaluation_scripts_folder_path=evaluation_scripts_folder_path,
            private_report_template_file_path=private_report_template_file_path,
            s3_bucket_name="pv-validation-hub-bucket",
            api_url=api_url,
            s3_url=s3_url,
            is_local=is_local,
        )
        r.insertData()
