import json
import logging
import os

from insert_analysis import InsertAnalysis

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    with open("routes.json", "r") as file:
        config = json.load(file)

        ########################################################################
        is_local = True
        is_force = False
        limit = 5
        is_dry_run = False
        use_cloud_files = False
        task_dir: str = "./analysis-tasks/time-shift-detection"
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
            task_dir, "data/ground-truth/"
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
