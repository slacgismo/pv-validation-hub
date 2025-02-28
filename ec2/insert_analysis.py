"""
Class for building out the data for insertion into the Postgres database,
including system metadata and file metadata.
"""

import json
from typing import Any, TypedDict
import pandas as pd
import os
import shutil
import argparse

from utility import (
    are_hashes_the_same,
    combine_hashes,
    get_data_from_api_to_df,
    get_file_hash,
    get_hash_for_list_of_files,
    hasAllColumns,
    post_data_to_api_to_df,
    request_to_API_w_credentials,
    upload_to_s3_bucket,
    with_credentials,
)

import logging


class SimpleFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            fmt="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = SimpleFormatter()
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)


class TaskConfig(TypedDict):
    category_name: str
    function_name: str
    comparison_type: str
    display_metrics: dict[str, str]
    performance_metrics: list[str]
    metrics_operations: dict[str, list[str]]
    allowable_kwargs: list[str]
    references_compare: list[str]
    public_results_table: str
    private_results_columns: list[str]


class InsertAnalysis:

    def __init__(
        self,
        markdown_files_folder_path: str,
        config_file_path: str,
        file_data_folder_path: str,
        validation_data_folder_path: str,
        evaluation_scripts_folder_path: str,
        sys_metadata_file_path: str,
        file_metadata_file_path: str,
        private_report_template_file_path: str,
        front_end_assets_folder_path: str,
        # validation_tests_file_path: str,
        s3_bucket_name: str,
        s3_task_bucket_name: str,
        api_url: str,
        s3_url: str,
        is_local: bool,
    ):

        config: TaskConfig = json.load(open(config_file_path, "r"))
        self.analysis_version: str = "1.0"
        self.config = config
        self.is_local = is_local

        self.api_url = api_url
        self.s3_url = s3_url

        # Fetching the data
        db_sys_metadata_df = get_data_from_api_to_df(
            self.api_url, "system_metadata/systemmetadata/", logger
        )
        db_file_metadata_df = get_data_from_api_to_df(
            self.api_url, "file_metadata/filemetadata/", logger
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
        self.new_sys_metadata_df: pd.DataFrame = pd.read_csv(  # type: ignore
            sys_metadata_file_path
        )
        self.new_file_metadata_df: pd.DataFrame = pd.read_csv(  # type: ignore
            file_metadata_file_path
        )

        self.analysis_id = None
        self.system_id_mapping: dict[int, int] = dict()
        self.file_id_mapping: dict[int, int] = dict()
        self.s3_bucket_name = s3_bucket_name
        self.s3_task_bucket_name = s3_task_bucket_name
        self.validation_data_folder_path = validation_data_folder_path

        self.markdown_files_folder_path = markdown_files_folder_path
        self.front_end_assets_folder_path = front_end_assets_folder_path
        self.data_files_hash = ""
        self.references_files_hash = ""
        self.combined_hash = ""
        self.db_hash = ""

    def hasAllValidNewAnalysisData(self, use_cloud_files: bool = False):
        """
        Check if we have all the required data to create a new analysis.

        Returns
        -------
        bool: True if we have all the required data, False otherwise.
        """

        is_valid: bool = True

        file_metadata_files: pd.Series[str] = self.new_file_metadata_df[
            "file_name"
        ]

        # are there any duplicates?
        for filename in file_metadata_files:
            # count how many times the filename appears in the list
            count = file_metadata_files[
                file_metadata_files == filename
            ].count()
            if count > 1:
                is_valid = False
                raise ValueError(
                    f"Duplicate file name {filename} in the file metadata."
                )

        sys_metadata_files: pd.Series[str] = self.new_sys_metadata_df["name"]

        # are there any duplicates?
        for filename in sys_metadata_files:
            # count how many times the filename appears in the list
            count = sys_metadata_files[sys_metadata_files == filename].count()
            if count > 1:
                is_valid = False
                raise ValueError(
                    f"Duplicate system name {filename} in the system metadata."
                )

        file_data_files = os.listdir(self.file_data_folder_path)

        if not all(file in file_data_files for file in file_metadata_files):
            is_valid = False
            raise ValueError(
                "The file metadata contains files that are not in the file data folder."
            )

        validation_data_files = os.listdir(self.validation_data_folder_path)

        if not all(
            file in validation_data_files for file in file_metadata_files
        ):
            is_valid = False
            raise ValueError(
                "The file metadata contains files that are not in the validation data folder."
            )

        template_file_exists = os.path.exists(
            self.private_report_template_file_path
        )

        if not template_file_exists:
            is_valid = False
            raise ValueError(
                "The private report template file does not exist."
            )

        required_markdown_files = [
            "banner.png",
            "cardCover.png",
            "description.md",
            "shortdesc.md",
            "SubmissionInstructions.md",
        ]

        markdown_files = os.listdir(self.markdown_files_folder_path)

        for file in required_markdown_files:
            if file not in markdown_files:
                is_valid = False
                raise ValueError(
                    f"Missing markdown file {file} in the markdown files folder."
                )

        logger.info(
            f"Frontend assets folder: {os.path.abspath(self.front_end_assets_folder_path)}"
        )

        front_end_analysis_assets_folder_exists = os.path.exists(
            os.path.join(self.front_end_assets_folder_path, "analysis")
        )

        if not front_end_analysis_assets_folder_exists:
            is_valid = False
            raise ValueError(
                "The analysis folder does not exist in the front end assets folder."
            )

        frontend_development_assets_folder_exists = os.path.exists(
            os.path.join(self.front_end_assets_folder_path, "development")
        )

        if not frontend_development_assets_folder_exists:
            is_valid = False
            raise ValueError(
                "The development folder does not exist in the front end assets folder."
            )

        logger.info("All files are in the right place.")

        return is_valid

    def getAllAnalyses(self) -> pd.DataFrame:
        """
        Get all analyses from the API.



        Returns
        -------
        List: List of all analyses.
        """

        df = get_data_from_api_to_df(self.api_url, "analysis/home", logger)

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
            specific_analysis = db_analysis_df[
                db_analysis_df["analysis_name"] == self.config["category_name"]
            ]
            db_analysis_id = specific_analysis["analysis_id"].values[0]
            analysis_version = specific_analysis["version"].values[0]
            db_hash = specific_analysis["hash"].values[0]
            logger.info(
                f'Analysis {self.config["category_name"]} already exists with id {db_analysis_id}'
            )
            self.analysis_id = db_analysis_id
            self.analysis_version = analysis_version
            self.db_hash = db_hash

        else:

            if force:
                logger.info("Force is True. Creating a new analysis.")

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

            # increment analysis version

            logger.info("display_errors", display_errors)
            logger.info(f"number of files: {len(self.new_file_metadata_df)}")

            body: dict[str, Any] = {
                "analysis_name": self.config["category_name"],
                "display_errors": display_errors,
                "total_files": len(self.new_file_metadata_df),
            }

            logger.info("body", body)

            res = post_data_to_api_to_df(
                self.api_url, "analysis/create/", body, logger
            )

            logger.info("Analysis created")
            self.analysis_id = res["analysis_id"].values[0]

    def createSystemMetadata(self, sys_metadata_df: pd.DataFrame):
        """
        Upload the system metadata to the API.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        """

        body = sys_metadata_df.to_json(orient="records")  # type: ignore
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
                logger.info(system["dc_capacity"])
                if system["dc_capacity"] is not None:
                    json_body["dc_capacity"] = system["dc_capacity"]

            logger.info(json_body)

            post_data_to_api_to_df(
                self.api_url,
                "system_metadata/systemmetadata/",
                json_body,
                logger,
            )

    def createFileMetadata(self, file_metadata_df: pd.DataFrame):
        """
        Upload the file metadata and validation tests to the API and S3.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        """

        body = file_metadata_df.to_json(orient="records")  # type: ignore
        metadata_json_list = json.loads(body)

        for metadata in metadata_json_list:

            json_body = {
                "system_id": metadata["system_id"],
                "file_name": metadata["file_name"],
                "timezone": metadata["timezone"],
                "data_sampling_frequency": metadata["data_sampling_frequency"],
                "issue": metadata["issue"],
                "subissue": metadata["subissue"],
                "file_hash": metadata["file_hash"],
            }

            logger.info(json_body)

            post_data_to_api_to_df(
                self.api_url, "/file_metadata/filemetadata/", json_body, logger
            )

            local_path = os.path.join(
                self.file_data_folder_path, metadata["file_name"]
            )
            upload_path = f'data_files/files/{metadata["file_name"]}'

            # upload metadata to s3
            upload_to_s3_bucket(
                self.s3_url,
                self.s3_bucket_name,
                local_path,
                upload_path,
                self.is_local,
            )

    def uploadValidationData(self):

        file_metadata_names: pd.Series[str] = self.new_file_metadata_df[
            "file_name"
        ]

        for file_name in file_metadata_names:
            # upload validation data to s3
            local_path = os.path.join(
                self.validation_data_folder_path, file_name
            )
            upload_path = (
                f"data_files/references/{str(self.analysis_id)}/{file_name}"
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
        for root, _, files in os.walk(evaluation_folder_path):
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
            self.api_url, "system_metadata/systemmetadata/", logger
        )

        self.db_sys_metadata_df = db_sys_metadata_df

        if db_sys_metadata_df.empty:
            return

        name_series: pd.Series[str] = pd.Series()
        system_id_series: pd.Series[int] = pd.Series()

        if hasAllColumns(db_sys_metadata_df, ["name", "system_id"]):

            name_series: pd.Series[str] = db_sys_metadata_df["name"]
            system_id_series: pd.Series[int] = db_sys_metadata_df["system_id"]

        # Create a dictionary of the system metadata IDs
        db_system_name_to_id_mapping = dict(
            zip(
                name_series,
                system_id_series,
            )
        )

        # TODO: Fix issue when the system_id is not found
        def map_system_id_to_db_system_id(ref_value: str, target_value: int):
            new_system_id = db_system_name_to_id_mapping.get(ref_value)
            if not new_system_id:
                raise ValueError("System ID not found")

            self.system_id_mapping[target_value] = int(new_system_id)
            return new_system_id

        df_new = self.new_sys_metadata_df.copy()

        # how do you create unique hash from columns from a dataframe?

        def process_row(row: pd.DataFrame) -> int:
            name: str = row["name"]  # type: ignore
            system_id: int = row["system_id"]  # type: ignore

            return map_system_id_to_db_system_id(name, system_id)

        df_new["system_id"] = df_new.apply(
            process_row,
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
            self.api_url, "file_metadata/filemetadata/", logger
        )

        self.db_file_metadata_df = db_file_metadata_df

        file_name_series: pd.Series[str] = db_file_metadata_df["file_name"]
        file_id_series: pd.Series[int] = db_file_metadata_df["file_id"]

        # Create a dictionary of the file metadata IDs
        db_file_name_to_id_mapping: dict[str, int] = dict(
            zip(
                file_name_series,
                file_id_series,
            )
        )

        def map_file_id_to_db_file_id(ref_value: str, target_value: int):
            new_file_id = db_file_name_to_id_mapping.get(ref_value)

            if not new_file_id:
                raise ValueError("File ID not found")

            self.file_id_mapping[target_value] = new_file_id
            return new_file_id

        df_new = self.new_file_metadata_df.copy()

        def process_row(row: pd.DataFrame) -> int:
            file_name: str = row["file_name"]  # type: ignore
            file_id: int = row["file_id"]  # type: ignore

            return map_file_id_to_db_file_id(file_name, file_id)

        df_new["file_id"] = df_new.apply(
            process_row,
            axis=1,
        )
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

        same_systems = pd.merge(  # type: ignore
            df_new, df_old, how="inner", on=["name", "latitude", "longitude"]
        )

        df_new = df_new[~df_new["name"].isin(list(same_systems["name"]))]  # type: ignore

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

        def addNAtoMissingColumns(df: pd.DataFrame, columns: list[str]):
            new_df = df.copy()
            for column in columns:
                if column not in df.columns:
                    new_df[column] = None
            return new_df

        # Return the system data ready for insertion
        df_modified = addNAtoMissingColumns(df_new, system_metadata_columns)
        logger.info(df_modified.head(5))
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
            ~df_new["file_name"].isin(list(overlapping_files["file_name"]))  # type: ignore
        ]

        df_new["system_id"] = df_new["system_id"].map(self.system_id_mapping)

        # Check if any system IDs are missing
        if df_new["system_id"].isna().any():  # type: ignore
            raise ValueError(
                "Some system IDs are missing from the system metadata dataframe."
            )

        # Fill in any missing values with "N/A"

        if "issue" not in df_new.columns:
            df_new["issue"] = "N/A"
        else:
            df_new["issue"] = df_new["issue"].fillna("N/A")  # type: ignore

        if "subissue" not in df_new.columns:
            df_new["subissue"] = "N/A"
        else:
            df_new["subissue"] = df_new["subissue"].fillna("N/A")  # type: ignore

        # hash the files

        for file_name in df_new["file_name"]:
            local_path = os.path.join(self.file_data_folder_path, file_name)
            file_hash = get_file_hash(local_path)
            df_new.loc[df_new["file_name"] == file_name, "file_hash"] = (
                file_hash
            )

        return df_new[
            [
                "system_id",
                "file_name",
                "timezone",
                "data_sampling_frequency",
                "issue",
                "subissue",
                "file_hash",
            ]
        ]

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

        overlapping_files = pd.merge(  # type: ignore
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
            self.api_url, "GET", endpoint=endpoint, logger=logger
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

        file_test_link: pd.Series[int] = self.new_file_metadata_df["file_id"]

        file_test_link.index.name = "test_id"  # type: ignore

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

    def updateFrontEndAssets(self):
        """
        Update the front end assets.
        """

        # Copy the markdown files to the new folder
        markdown_files = os.listdir(self.markdown_files_folder_path)

        valid_file_types = ["md", "png", "PNG"]

        filtered_assets = [
            file
            for file in markdown_files
            if file.split(".")[-1] in valid_file_types
        ]
        logger.info(f"filtered_assets {filtered_assets}")

        analysis_assets_folder = os.path.join(
            self.front_end_assets_folder_path, "analysis"
        )

        id_analysis_assets_folder = os.path.join(
            analysis_assets_folder, str(self.analysis_id)
        )

        # Clear any existing assets associated with the analysis in the front end assets folder

        if os.path.exists(id_analysis_assets_folder):
            shutil.rmtree(id_analysis_assets_folder)

        # Create the new folder
        os.makedirs(id_analysis_assets_folder)

        # Copy the files to the new folder
        for file in filtered_assets:
            shutil.copy(
                os.path.join(self.markdown_files_folder_path, file),
                os.path.join(id_analysis_assets_folder, file),
            )

    def updateMetadataWithLimit(self, limit: int):
        limit_new_file_metadata_df = self.new_file_metadata_df.head(limit)

        file_sys_ids: pd.Series[int] = limit_new_file_metadata_df["system_id"]

        limit_new_sys_metadata_df = self.new_sys_metadata_df[
            self.new_sys_metadata_df["system_id"].isin(file_sys_ids)  # type: ignore
        ]

        self.new_file_metadata_df = limit_new_file_metadata_df
        self.new_sys_metadata_df = limit_new_sys_metadata_df

        self.config["category_name"] = (
            f"{self.config['category_name']} - {limit} File(s)"
        )

    def createHashofFiles(self):
        """
        Create a hash of the data files for the analysis.
        """

        data_files = os.listdir(self.file_data_folder_path)

        hash_for_data_files = get_hash_for_list_of_files(
            [
                os.path.join(self.file_data_folder_path, file)
                for file in data_files
            ]
        )

        logger.info(f"Data files hash: {hash_for_data_files}")

        self.data_files_hash = hash_for_data_files

        references_files = os.listdir(self.validation_data_folder_path)

        hash_for_references_files = get_hash_for_list_of_files(
            [
                os.path.join(self.validation_data_folder_path, file)
                for file in references_files
            ]
        )

        logger.info(f"Data files hash: {hash_for_references_files}")

        self.references_files_hash = hash_for_references_files

        self.combined_hash = combine_hashes(
            [self.data_files_hash, self.references_files_hash]
        )

        logger.info(f"Combined hash: {self.combined_hash}")

        return self.combined_hash

    def updateAnalysisHash(self, hash: str):

        if are_hashes_the_same(self.db_hash, hash):
            logger.info(
                "The hash of the files are the same as the hash in the database. No need to update the analysis version."
            )
            return

        logger.info(
            "The hash of the files are different from the hash in the database. Updating the analysis version."
        )

        semver = self.analysis_version.split(".")
        major = semver[0]
        minor = semver[1]

        if self.db_hash == "" and self.analysis_version == "1.0":
            self.analysis_version = "1.0"
        else:
            self.analysis_version = f"{major}.{int(minor) + 1}"

        logger.info(f"New analysis task version: {self.analysis_version}")

        body = {
            "hash": hash,
            "version": self.analysis_version,
        }

        response = with_credentials(self.api_url, logger)(
            request_to_API_w_credentials
        )(
            self.api_url,
            "PUT",
            endpoint=f"analysis/{self.analysis_id}/update",
            data=body,
            logger=logger,
        )
        logger.info(response)
        return response

    def insertData(self, use_cloud_files: bool = False, force: bool = False):
        """
        Insert all the data into the API and S3.
        """

        logger.info("Creating analysis")
        db_analyses_df = self.getAllAnalyses()
        self.createAnalysis(db_analyses_df, force)

        if not self.analysis_id:
            raise ValueError("Analysis ID not found or created.")

        logger.info(f"Created analysis with ID {self.analysis_id}")

        # exit()
        logger.info("Creating system metadata")
        new_sys_metadata_df = self.buildSystemMetadata()
        self.createSystemMetadata(new_sys_metadata_df)
        self.updateSystemMetadataIDs()
        logger.info("System metadata created")

        logger.info("Creating file metadata")
        new_file_metadata_df = self.buildFileMetadata()
        self.createFileMetadata(new_file_metadata_df)
        self.updateFileMetadataIDs()
        self.uploadValidationData()
        logger.info("File metadata created")

        # Create hash of the data files
        hash = self.createHashofFiles()

        # Compare the hashes and update task version if necessary
        self.updateAnalysisHash(hash)

        logger.info("Creating evaluation scripts")
        self.prepareFileTestLinker()
        self.prepareConfig()
        self.prepareTemplate()
        self.createEvaluationScripts()
        logger.info("Evaluation scripts created")

        logger.info("Update assets for front end")
        self.updateFrontEndAssets()
        logger.info("Front end assets updated")

        logger.info("Data inserted successfully")

        logger.warning(
            "If you are running this in a development environment without the `docker compose up --watch` command, you will need to manually rebuild the front end image and restart the container to see the changes."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert analysis data")
    parser.add_argument(
        "--dry-run",
        help="Run in dry-run mode",
        default=False,
    )
    parser.add_argument(
        "--force",
        help="Force the operation",
        default=False,
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of records",
        default=0,
    )
    parser.add_argument(
        "--prod",
        help="Set to production mode",
        default=False,
    )
    parser.add_argument(
        "--dir",
        help="Directory of the task",
    )
    parser.add_argument(
        "--use-cloud-files",
        help="Data files for task are local or in S3",
    )

    args, unknown = parser.parse_known_args()
    logger.info(dict(args._get_kwargs()))

    def convert_bool(val: str) -> bool:
        if val == "True":
            return True
        elif val == "False":
            return False
        else:
            raise ValueError(f"Invalid boolean value {val}")

    def convert_int(val: str) -> int:
        try:
            return int(val)
        except ValueError:
            raise ValueError(f"Invalid integer value {val}")

    with open("routes.json", "r") as file:
        config = json.load(file)

        ########################################################################
        is_local = not convert_bool(args.prod)
        is_force = convert_bool(args.force)
        limit = convert_int(args.limit)
        is_dry_run = convert_bool(args.dry_run)
        use_cloud_files = convert_bool(args.use_cloud_files)
        task_dir: str = args.dir
        ########################################################################

        logger.info(f"is_dry_run: {is_dry_run}")
        logger.info(f"is_force: {is_force}")
        logger.info(f"limit: {limit}")
        logger.info(f"is_local: {is_local}")
        logger.info(f"use_cloud_files: {use_cloud_files}")
        logger.info(f"task_dir: {task_dir}")

        if not os.path.exists(task_dir):
            raise ValueError(f"Directory {task_dir} does not exist")

        api_url = config["local"]["api"] if is_local else config["prod"]["api"]
        s3_url = config["local"]["s3"] if is_local else config["prod"]["s3"]

        config_file_path = os.path.join(task_dir, "config.json")
        file_data_folder_path = os.path.join(task_dir, "data/files/")
        evaluation_scripts_folder_path = "./evaluation_scripts/"
        sys_metadata_file_path = os.path.join(
            task_dir, "data/system_metadata.csv"
        )
        file_metadata_file_path = os.path.join(
            task_dir, "data/file_metadata.csv"
        )
        validation_data_folder_path = os.path.join(
            task_dir, "data/references/"
        )
        private_report_template_file_path = os.path.join(
            task_dir, "template.py"
        )

        analysis_markdown_files_folder_path = os.path.join(task_dir, "assets")
        front_end_assets_folder_path = "./front_end_assets"

        analysis_instance = InsertAnalysis(
            markdown_files_folder_path=analysis_markdown_files_folder_path,
            config_file_path=config_file_path,
            file_data_folder_path=file_data_folder_path,
            sys_metadata_file_path=sys_metadata_file_path,
            file_metadata_file_path=file_metadata_file_path,
            validation_data_folder_path=validation_data_folder_path,
            evaluation_scripts_folder_path=evaluation_scripts_folder_path,
            private_report_template_file_path=private_report_template_file_path,
            front_end_assets_folder_path=front_end_assets_folder_path,
            s3_bucket_name="pv-validation-hub-bucket",
            s3_task_bucket_name="pv-validation-hub-task-data-bucket",
            api_url=api_url,
            s3_url=s3_url,
            is_local=is_local,
        )

        if limit > 0:
            analysis_instance.updateMetadataWithLimit(limit)

        if not analysis_instance.hasAllValidNewAnalysisData(
            use_cloud_files=use_cloud_files
        ):
            raise ValueError("Data is not valid")

        if not is_local:
            response = input(
                "Are you sure you want to create/update a task on production? (yes/no): "
            )
            if response.lower() != "yes":
                logger.info("Exiting...")
                exit()

        if is_dry_run:
            logger.info("Dry run mode enabled. No data will be inserted.")
        else:
            analysis_instance.insertData(
                use_cloud_files=use_cloud_files,
                force=is_force,
            )
