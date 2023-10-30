"""
Class for building out the data for insertion into the Postgres database,
including system metadata and file metadata.
"""

import pandas as pd
import os
import shutil

class InsertAnalysis:

    def __init__(self,
                 db_sys_metadata_df,
                 db_file_metadata_df,
                 config_file_path,
                 file_data_path,
                 sys_metadata_file_path,
                 file_metadata_file_path):
        self.db_sys_metadata_df = db_sys_metadata_df
        self.db_file_metadata_df = db_file_metadata_df
        self.config_file_path = config_file_path
        self.file_data_path = file_data_path
        self.new_sys_metadata_df = pd.read_csv(sys_metadata_file_path)
        self.new_file_metadata_df = pd.read_csv(file_metadata_file_path)

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
        overlapping_systems = pd.merge(self.new_sys_metadata_df[[
            'name', 'latitude', 'longitude']],
            self.db_sys_metadata_df[['name', 'latitude', 'longitude']],
            on=['name', 'latitude', 'longitude'])
        # Remove the repeat systems from the metadata we want to insert
        self.new_sys_metadata_df = self.new_sys_metadata_df[
            ~self.new_sys_metadata_df[
                'name'].isin(list(overlapping_systems['name']))]
        # Get the highest system_id and then increment up from there
        max_system_id = self.db_sys_metadata_df.system_id.max() + 1
        system_ids = [*range(max_system_id,
                             max_system_id + len(self.new_sys_metadata_df))]
        self.new_sys_metadata_df['system_id'] = system_ids
        # Return the system data ready for insertion
        return self.new_sys_metadata_df[['system_id', 'name',
                                         'azimuth', 'tilt', 'elevation',
                                         'latitude', 'longitude',
                                         'tracking']]
    
    def getOverlappingFiles(self):
        """
        Return a dataframe files that are in both the new load and previously
        entered into the database.
        """
        overlapping_files = pd.merge(self.new_file_metadata_df[['file_name']],
                                     self.db_file_metadata_df[['file_name', 'file_id']],
                                     on=['file_name'])
        return overlapping_files
        

    def buildFileMetadata(self, s3_path):
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
        overlapping_files = self.getOverlappingFiles()
        # Remove the repeat systems from the metadata we want to insert
        self.new_file_metadata_df = self.new_file_metadata_df[
            ~self.new_file_metadata_df[
                'file_name'].isin(list(overlapping_files['file_name']))]
        # Get the highest file_id and then increment up from there
        max_file_id = self.db_file_metadata_df.file_id.max() + 1
        file_ids = [*range(max_file_id,
                           max_file_id + len(self.new_file_metadata_df))]
        self.new_file_metadata_df['file_id'] = file_ids
        # Build out the S3 path for each file name
        self.new_file_metadata_df['base_file_name'] = \
            self.new_file_metadata_df['file_name']
        self.new_file_metadata_df['file_name'] = [
            os.path.join(s3_path, x) for x in list(
                self.new_file_metadata_df['file_name'])]
        return self.new_file_metadata_df[['file_id', 'system_id', 'file_name',
                                         'timezone', 'data_sampling_frequency',
                                          'issue']]

    def buildS3fileInserts(self):
        """
        Build out the list of lists for routing the associated files into S3.
        """
        file_insert_list = [(os.path.join(self.file_data_path, x), y)
                            for x, y in
                            zip(self.new_file_metadata_df['base_file_name'],
                                self.new_file_metadata_df['file_name'])]
        return file_insert_list

    def insertConfig(self, evaluation_folder_path):
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
        # Check the sub-folders in the evaluation_folder_path
        subfolders = [int(os.path.basename(f.path)) for f in
                      os.scandir(evaluation_folder_path) if f.is_dir()]
        new_analysis_id = max(subfolders) + 1
        # Create a new folder for the analysis
        new_folder = os.path.join(evaluation_folder_path, str(new_analysis_id))
        os.makedirs(new_folder)
        # Drop the config JSON into the new folder
        shutil.copyfile(self.config_file_path, os.path.join(new_folder,
                                                            "config.json"))
        # TODO: any additional files we'd want to pipe over???
        return new_folder

    def generateFileTestLinker(self, new_evaluation_folder):
        """
        Generate the file test linker and drop it into the new evaluation
        folder.

        Parameters
        ----------
        new_evaluation_folder: String. File path to the evaluation subfolder
            for a particular analysis (ex: /1/, /2/, etc). Ths folder will
            contain the config JSON.
        """
        file_test_link = pd.Series(self.new_file_metadata_df['file_id'],
                                   name='file_id')
        # Add back any files that were previously entered into the DB and
        # have existing file ID's
        overlapping_files = self.getOverlappingFiles()
        if len(overlapping_files) > 0:
            file_test_link = file_test_link.append(overlapping_files['file_id'])
        # Write to the folder
        file_test_link.to_csv(os.path.join(new_evaluation_folder,
                                           "file_test_link.csv"))
        return


db_metadata_df = pd.read_csv(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/system_metadata.csv")

db_file_metadata_df = pd.read_csv(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/file_metadata.csv")


r = InsertAnalysis(db_metadata_df,
                   db_file_metadata_df,
                   config_file_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/config.json",
                   file_data_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/file_data/",
                   sys_metadata_file_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/system_metadata.csv",
                   file_metadata_file_path="C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/file_metadata.csv")
sys_data_insert = r.buildSystemMetadata()
file_data_insert = r.buildFileMetadata(s3_path="s3://eval/")
s3_insert_list = r.buildS3fileInserts()
# Create folder and insert the config
new_folder = r.insertConfig(
    "C:/Users/kperry/Documents/source/repos/pv-validation-hub/s3Emulator/pv-validation-hub-bucket/evaluation_scripts/")
r.generateFileTestLinker(new_folder)
