"""
Class for building out the data for insertion into the Postgres database,
including system metadata and file metadata.
"""

from hmac import new
import json
import pandas as pd
import os
import shutil
import requests
import boto3
import sys
import requests


API_URI = "http://api:8005"


def hasAllColumns(df, cols: list):
    """
    Check if the dataframe has the required columns for overlap
    checking.
    """
    return all(col in df.columns for col in cols)


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return (
        "AWS_EXECUTION_ENV" not in os.environ
        and "ECS_CONTAINER_METADATA_URI" not in os.environ
        and "ECS_CONTAINER_METADATA_URI_V4" not in os.environ
    )


def upload_to_s3_bucket(bucket_name, local_path, upload_path):

    if is_local():
        upload_path = os.path.join(bucket_name, upload_path)
        s3_file_full_path = "http://s3:5000/put_object/" + upload_path
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
                    "http://s3:5000/put_object/", "http://s3:5000/get_object/"
                )
    else:
        """Upload file to S3 bucket and return object URL"""
        s3 = boto3.client("s3")

        try:
            s3.upload_file(local_path, bucket_name, upload_path)
        except:
            return None

        bucket_location = boto3.client("s3").get_bucket_location(Bucket=bucket_name)
        object_url = "https://{}.s3.{}.amazonaws.com/{}".format(
            bucket_name, bucket_location["LocationConstraint"], upload_path
        )
        return object_url


class InsertAnalysis:

    def __init__(
        self,
        db_sys_metadata_df: pd.DataFrame,
        db_file_metadata_df: pd.DataFrame,
        config_file_path: str,
        file_data_path: str,
        validation_data_path: str,
        evaluation_scripts_path: str,
        sys_metadata_file_path: str,
        file_metadata_file_path: str,
        validation_tests_file_path: str,
        analysis_id: int | None = None,
        system_id_mapping: dict = dict(),
        s3_bucket_name: str = "pv-validation-hub-bucket",
        config: dict = dict(),
    ):

        config = json.load(open(config_file_path, "r"))

        self.config = config
        self.db_sys_metadata_df = db_sys_metadata_df
        self.db_file_metadata_df = db_file_metadata_df
        self.config_file_path = config_file_path
        self.file_data_path = file_data_path
        self.evaluation_scripts_path = evaluation_scripts_path
        self.validation_tests_file_path = validation_tests_file_path
        self.new_sys_metadata_df = pd.read_csv(sys_metadata_file_path)
        self.new_file_metadata_df = pd.read_csv(file_metadata_file_path)
        self.validation_tests_df = pd.read_csv(validation_tests_file_path)
        self.analysis_id = None
        self.system_id_mapping = system_id_mapping
        self.s3_bucket_name = s3_bucket_name
        self.validation_data_path = validation_data_path

    # Create and upload to the API and S3
    def createAnalysis(self, max_concurrent_submission_evaluation: int):
        """
        Create a new analysis in the API.
        """
        url = f"{API_URI}/analysis/create/"

        body = {
            "analysis_name": self.config["category_name"],
            "max_concurrent_submission_evaluation": max_concurrent_submission_evaluation,
        }
        response = requests.post(url, json=body)
        if not response.ok:
            raise ValueError(
                f"Error creating analysis. Status code: {response.status_code}"
            )
        data = response.json()
        return data

    def createSystemMetadata(self, sys_metadata_df: pd.DataFrame):
        """
        Upload the system metadata to the API.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        """

        url = f"{API_URI}/system_metadata/systemmetadata/"

        body = sys_metadata_df.to_json(orient="records")
        systems_json_list = json.loads(body)

        for system in systems_json_list:

            json_body = {
                # "system_id": system["system_id"],
                "name": system["name"],
                "azimuth": system["azimuth"],
                "tilt": system["tilt"],
                "elevation": system["elevation"],
                "latitude": system["latitude"],
                "longitude": system["longitude"],
                "tracking": system["tracking"],
                "dc_capacity": system["dc_capacity"],
            }

            print(json_body)

            response = requests.post(
                url, json=json_body, headers={"Content-Type": "application/json"}
            )
            if not response.ok:
                raise ValueError(
                    f"Error creating system metadata. Status code: {response.status_code}"
                )
            data = response.json()
            print(data)

    def createFileMetadata(self, file_metadata_df: pd.DataFrame):
        """
        Upload the file data to the S3 bucket.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        """

        url = f"{API_URI}/file_metadata/filemetadata/"
        print("createFileMetadata")

        body = file_metadata_df.to_json(orient="records")
        metadata_json_list = json.loads(body)

        for metadata in metadata_json_list:

            json_body = {
                # "file_id": metadata["file_id"],
                "system_id": metadata["system_id"],
                "file_name": metadata["file_name"],
                "timezone": metadata["timezone"],
                "data_sampling_frequency": metadata["data_sampling_frequency"],
                "issue": metadata["issue"],
                "subissue": metadata["subissue"],
            }

            print(json_body)

            response = requests.post(
                url, json=json_body, headers={"Content-Type": "application/json"}
            )
            if not response.ok:
                raise ValueError(
                    f"Error creating file metadata. Status code: {response.status_code} {response.content}"
                )
            data = response.json()
            print(data)

            local_path = os.path.join(self.file_data_path, metadata["file_name"])
            upload_path = f'data_files/analytical/{metadata["file_name"]}'

            # upload metadata to s3
            upload_to_s3_bucket(self.s3_bucket_name, local_path, upload_path)

            # upload validation data to s3
            local_path = os.path.join(self.validation_data_path, metadata["file_name"])
            upload_path = f'data_files/analytical/{metadata["file_name"]}'
            upload_to_s3_bucket(self.s3_bucket_name, local_path, upload_path)

    def createValidationData(self):
        """
        Upload the validation data to the API.

        Parameters
        ----------
        validation_tests_df: Pandas dataframe. Dataframe of the validation
            tests.
        """
        url = f"{API_URI}/validation_tests/upload_csv/"

        file = open(self.validation_tests_file_path, "r")

        response = requests.post(url, files={"file": file})
        if not response.ok:
            raise ValueError(
                f"Error creating validation tests. Status code: {response.status_code}. {response.content}"
            )
        data = response.json()
        print(data)

    def createEvaluationScripts(self):
        """
        Upload the evaluation scripts to the S3 bucket.

        Parameters
        ----------
        eval_folder: String. File path to the evaluation subfolder for a
            particular analysis (ex: /1/, /2/, etc). Ths folder will contain
            the config JSON.
        """

        evaluation_folder_path = os.path.join(
            self.evaluation_scripts_path, f"{str(self.analysis_id)}/"
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
                upload_to_s3_bucket(self.s3_bucket_name, local_path, upload_path)

    def buildSystemMetadata(self):
        """
        Check what exists in the system_metadata table to see
        if we have overlap with the systems we want to insert. Build out
        the system metadata for insert and return the dataframe for
        DB insert.

        Returns
        -------
        Pandas dataframe: Pandas df ready for insert into the system_metadata
            table.
        """

        # Check cases to determine if we have overlap, using the name,
        # latitude, and longitude fields

        df_new = self.new_sys_metadata_df
        df_old = self.db_sys_metadata_df

        if not hasAllColumns(df_new, ["name", "latitude", "longitude"]):
            raise ValueError(
                "The new system metadata dataframe does not have the required columns. name, latitude, and longitude are required."
            )

        if not hasAllColumns(df_old, ["name", "latitude", "longitude"]):
            df_old = pd.DataFrame([], columns=["name", "latitude", "longitude"])

        db_system_name_to_id_mapping = (
            dict(zip(df_old["name"], df_old["system_id"]))
            if not df_old.empty
            else dict()
        )

        same_systems = pd.merge(
            df_new, df_old, how="inner", on=["name", "latitude", "longitude"]
        )

        # If there are no systems in the database, we can just start at 1
        max_system_id = df_old["system_id"].max() + 1 if not same_systems.empty else 1

        counter = 0

        def map_system_id_to_db_system_id(self, ref_value, target_value):
            nonlocal counter
            new_system_id = db_system_name_to_id_mapping.get(ref_value)

            if not new_system_id:
                new_system_id = max_system_id + counter
                counter += 1

            self.system_id_mapping[target_value] = new_system_id
            return new_system_id

        df_new["system_id"] = df_new.apply(
            lambda row: map_system_id_to_db_system_id(
                self, row["name"], row["system_id"]
            ),
            axis=1,
        )

        df_new = df_new[~df_new["name"].isin(list(same_systems["name"]))]

        self.new_sys_metadata_df = df_new

        # Return the system data ready for insertion
        return self.new_sys_metadata_df[
            [
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
        ]

    def buildFileMetadata(self):
        """
        Check for duplicates in the file metadata table. Build nonduplicated
        file metadata for insert into the file_metadata table.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.

        Returns
        -------
        Pandas dataframe: Pandas df ready for insert into the file_metadata
            table.
        """

        overlapping_files = self.getOverlappingMetadataFiles()
        # Remove the repeat systems from the metadata we want to insert
        self.new_file_metadata_df = self.new_file_metadata_df[
            ~self.new_file_metadata_df["file_name"].isin(
                list(overlapping_files["file_name"])
            )
        ]

        self.new_file_metadata_df["system_id"] = self.new_file_metadata_df[
            "system_id"
        ].map(self.system_id_mapping)

        # Fill in any missing values with "N/A"
        self.new_file_metadata_df["issue"] = self.new_file_metadata_df["issue"].fillna(
            "N/A"
        )

        self.new_file_metadata_df["subissue"] = self.new_file_metadata_df[
            "subissue"
        ].fillna("N/A")

        return self.new_file_metadata_df[
            [
                "file_id",
                "system_id",
                "file_name",
                "timezone",
                "data_sampling_frequency",
                "issue",
                "subissue",
            ]
        ]

    def buildValidationTests(self):
        """
        Build out the validation tests for insert into the validation_tests
        table.

        Returns
        -------
        Pandas dataframe: Pandas df ready for insert into the validation_tests
            table.
        """

        validation_tests_df = self.validation_tests_df[
            ["category_name", "performance_metrics", "function_name"]
        ]

        return validation_tests_df

    def buildS3fileInserts(self):
        """
        Build out the list of lists for routing the associated files into S3.
        """
        file_insert_list = [
            (os.path.join(self.file_data_path, x), y)
            for x, y in zip(
                self.new_file_metadata_df["file_name"],
                self.new_file_metadata_df["s3_file_path"],
            )
        ]

        return file_insert_list

    def getOverlappingMetadataFiles(self):
        """
        Return a dataframe files that are in both the new load and previously
        entered into the database.
        """
        df_new = self.new_file_metadata_df
        df_old = self.db_file_metadata_df

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
        Create new folder path and insert the associated config.json in that
        path. In the future, we can add additional files for the insertion.

        Parameters
        ----------
        evaluation_folder_path: String. File path to the evaluation folder,
            which includes all of the analysis subfolders (/1/, /2/, etc)

        Returns
        -------
        new_folder: String. File path where we're going to insert data for the
            particular analysis (example:
            ./s3Emulator/pv-validation-hub-bucket/evaluation_scripts/1/)
        """
        evaluation_folder_path = os.path.join(
            self.evaluation_scripts_path, str(self.analysis_id)
        )
        if not os.path.exists(evaluation_folder_path):
            os.makedirs(evaluation_folder_path)
        # Drop the config JSON into the new folder

        shutil.copy(self.config_file_path, evaluation_folder_path)

        return evaluation_folder_path

    def getNewAnalysisId(self, api_url):

        full_url = api_url + "/analysis/home"

        print(full_url)

        r = requests.get(full_url)
        if r.status_code != 200:
            raise ValueError(
                f"Error getting the home page from the API. Status code: {r.status_code}"
            )
        data = r.json()
        new_analysis_id = len(data) + 1

        self.analysis_id = new_analysis_id

        return new_analysis_id

    def prepareFileTestLinker(self):
        """
        Generate the file test linker and drop it into the new evaluation
        folder.

        Parameters
        ----------
        new_evaluation_folder: String. File path to the evaluation subfolder
            for a particular analysis (ex: /1/, /2/, etc). Ths folder will
            contain the config JSON.
        """
        # Retrieve all file metadata from the database. This will contain all the file metadata that was just inserted.
        url = f"{API_URI}/file_metadata/filemetadata/"

        response = requests.get(url)
        if not response.ok:
            raise ValueError(
                f"Error retreiving db file metadata. Status code: {response.status_code}. {response.content}"
            )
        data = response.json()
        print(data)

        db_filemetadata_df = pd.DataFrame(data)
        print(db_filemetadata_df)

        file_test_link = db_filemetadata_df["file_id"]

        file_test_link.index.name = "test_id"

        local_file_path = os.path.join(
            self.evaluation_scripts_path, str(self.analysis_id)
        )

        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path)

        # Write to the folder
        file_test_link_path = file_test_link.to_csv(
            os.path.join(local_file_path, "file_test_link.csv")
        )
        return file_test_link_path

    def insertData(self, api_url: str):
        """
        Insert the system metadata, file metadata, and S3 file data into the
        Postgres database. Also, create a new folder for the evaluation
        analysis and drop in the config JSON and file test linker.

        Parameters
        ----------
        s3_path: String. S3 path that we want to write the files to.
        evaluation_folder_path: String. File path to the evaluation folder,
            which includes all of the analysis subfolders (/1/, /2/, etc)
        """
        sys_metadata_df = self.buildSystemMetadata()
        file_metadata_df = self.buildFileMetadata()
        self.buildValidationTests()

        self.getNewAnalysisId(api_url)

        self.createAnalysis(100)
        self.createSystemMetadata(sys_metadata_df)
        self.createFileMetadata(file_metadata_df)
        self.createValidationData()

        self.prepareFileTestLinker()
        self.prepareConfig()
        self.createEvaluationScripts()


if __name__ == "__main__":
    pass
    # db_metadata_df = pd.read_csv("./time-shift-validation-hub/data/system_metadata.csv")

    # db_file_metadata_df = pd.read_csv(
    #     "./time-shift-validation-hub/data/file_metadata.csv"
    # )

    # r = InsertAnalysis(
    #     db_metadata_df,
    #     db_file_metadata_df,
    #     config_file_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/config.json",
    #     file_data_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/file_data/",
    #     sys_metadata_file_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/system_metadata.csv",
    #     file_metadata_file_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/file_metadata.csv",
    # )
    # sys_data_insert = r.buildSystemMetadata()
    # file_data_insert = r.buildFileMetadata(s3_path="s3://eval/")
    # s3_insert_list = r.buildS3fileInserts()
    # # Create folder and insert the config
    # new_folder = r.insertConfig(
    #     "C:/Users/kperry/Documents/source/repos/pv-validation-hub/s3Emulator/pv-validation-hub-bucket/evaluation_scripts/"
    # )
    # r.generateFileTestLinker(new_folder)
