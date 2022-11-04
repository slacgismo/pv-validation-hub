import importlib
import subprocess
import traceback
import zipfile
import requests
import sys
import os
import tempfile
import logging
import django
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'valhub.settings'

django.setup()

from analyses.models import Analysis

BASE_TEMP_DIR = tempfile.mkdtemp()
COMPUTE_DIRECTORY_PATH = os.path.join(BASE_TEMP_DIR, "compute")
ANALYSIS_DATA_BASE_DIR = os.path.join(COMPUTE_DIRECTORY_PATH, "analysis_data")
SUBMISSION_DATA_BASE_DIR = os.path.join(
    COMPUTE_DIRECTORY_PATH, "submission_files")
ANALYSIS_DATA_DIR = os.path.join(
    ANALYSIS_DATA_BASE_DIR, "analysis_{analysis_id}")
ANALYSIS_IMPORT_STRING = "analysis_data.analysis_{analysis_id}"

WORKER_LOGS_PREFIX = "WORKER_LOG"
SUBMISSION_LOGS_PREFIX = "SUBMISSION_LOG"

EVALUATION_SCRIPTS = {}

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_dir(directory):
    """
    Creates a directory if it does not exists
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_dir_as_python_package(directory):
    """
    Create a directory and then makes it a python
    package by creating `__init__.py` file.
    """
    create_dir(directory)
    init_file_path = os.path.join(directory, "__init__.py")
    with open(init_file_path, "w") as init_file:  # noqa
        # to create empty file
        pass


def extract_zip_file(download_location, extract_location):
    """
    Helper function to extract zip file
    Params:
        * `download_location`: Location of zip file
        * `extract_location`: Location of directory for extracted file
    """
    zip_ref = zipfile.ZipFile(download_location, "r")
    zip_ref.extractall(extract_location)
    zip_ref.close()


def delete_zip_file(download_location):
    """
    Helper function to remove zip file from location `download_location`
    Params:
        * `download_location`: Location of file to be removed.
    """
    try:
        os.remove(download_location)
    except Exception as e:
        logger.error(
            "{} Failed to remove zip file {}, error {}".format(
                WORKER_LOGS_PREFIX, download_location, e
            )
        )
        traceback.print_exc()

# def return_file_url_per_environment(url):
#     if (
#         DJANGO_SETTINGS_MODULE == "settings.dev"
#         or DJANGO_SETTINGS_MODULE == "settings.test"
#     ):
#         base_url = (
#             f"http://{settings.DJANGO_SERVER}:{settings.DJANGO_SERVER_PORT}"
#         )
#         url = "{0}{1}".format(base_url, url)
#     return url


def download_and_extract_zip_file(url, download_location, extract_location):
    """
    * Function to extract download a zip file, extract it and then removes the zip file.
    * `download_location` should include name of file as well.
    """
    try:
        # TODO: where to store evaluation script
        response = requests.get(url, stream=True)
    except Exception as e:
        logger.error(
            "{} Failed to fetch file from {}, error {}".format(
                WORKER_LOGS_PREFIX, url, e
            )
        )
        response = None

    if response and response.status_code == 200:
        with open(download_location, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        # extract zip file
        extract_zip_file(download_location, extract_location)
        # delete zip file
        delete_zip_file(download_location)


def extract_analysis_data(analysis):
    analysis_data_directory = ANALYSIS_DATA_DIR.format(
        analysis_id=analysis.analysis_id
    )
    # create analysis directory as package
    create_dir_as_python_package(analysis_data_directory)

    # analysis.evaluation_script.url
    evaluation_script_url = analysis.evaluation_script_url
    # evaluation_script_url = return_file_url_per_environment(
    #     evaluation_script_url
    # )

    # download and extract analysis
    # requirements.txt, evaluation_script, annotation_file
    analysis_zip_file = os.path.join(
        analysis_data_directory, "analysis_{}.zip".format(analysis.analysis_id)
    )
    download_and_extract_zip_file(
        evaluation_script_url, analysis_zip_file, analysis_data_directory
    )

    # install requirements
    try:
        requirements_location = os.path.join(
            analysis_data_directory, "requirements.txt")
        if os.path.isfile(requirements_location):
            subprocess.check_output(
                [sys.executable, "-m", "pip", "install", "-r", requirements_location])
        else:
            logger.info(
                "No custom requirements for analysis {}".format(analysis.analysis_id))
    except Exception as e:
        logger.error(e)

    # import analysis as a module
    try:
        importlib.invalidate_caches()
        analysis_module = importlib.import_module(
            ANALYSIS_IMPORT_STRING.format(analysis_id=analysis.analysis_id)
        )
        EVALUATION_SCRIPTS[analysis.analysis_id] = analysis_module
    except Exception:
        logger.exception(
            "{} Exception raised while creating Python module for analysis_id: {}".format(
                WORKER_LOGS_PREFIX, analysis.analysis_id
            )
        )
        raise


def load_analysis(analysis):
    # data, eval_script
    create_dir_as_python_package(ANALYSIS_DATA_BASE_DIR)
    # phases = challenge.challengephase_set.all()
    extract_analysis_data(analysis)


def load_analysis_and_return_max_submissions(q_params):
    try:
        analysis = Analysis.objects.get(**q_params)
    except Analysis.DoesNotExist:
        logger.exception(
            "{} Analysis with pk {} doesn't exist".format(
                WORKER_LOGS_PREFIX, q_params["pk"]
            )
        )
        raise
    load_analysis(analysis)
    maximum_concurrent_submissions = analysis.max_concurrent_submission_evaluation
    return maximum_concurrent_submissions, analysis


def run_submission(analysis_id, submission, user_annotation_file_path):
    """
    * receives a analysis id and user annotation file path
    * checks whether the corresponding evaluation script for the analysis exists or not
    * checks the above for annotation file
    * calls evaluation script via subprocess passing annotation file and user_annotation_file_path as argument
    """
    annotation_file_path = ""
    try:
        submission_output = EVALUATION_SCRIPTS[analysis_id].evaluate(
            annotation_file_path,
            user_annotation_file_path,
            # submission_metadata=submission_serializer.data,
        )
        """
        A submission will be marked successful only if it is of the format
            {
               "result":[
                  {
                     "split_test":{
                        "execution_time":30,
                        "metric":50,
                     }
                  }
               ],
               "submission_metadata": {'foo': 'bar'},
               "submission_result": ['foo', 'bar'],
            }
        """
        print(submission_output)
    except Exception as e:
        print(e)


def main():
    logger.info(
        "{} Using {} as temp directory to store data".format(
            WORKER_LOGS_PREFIX, BASE_TEMP_DIR
        )
    )
    create_dir_as_python_package(COMPUTE_DIRECTORY_PATH)
    sys.path.append(COMPUTE_DIRECTORY_PATH)

    # q_params = {}
    # q_params["end_date__gt"] = timezone.now()

    # # primary key
    # analysis_pk = os.environ.get("ANALYSIS_PK")
    # if analysis_pk:
    #     q_params["pk"] = analysis_pk

    # load analysis
    # maximum_concurrent_submissions, analysis = load_analysis_and_return_max_submissions(
    #     q_params)

    # create submission directory

    # create message queue

    # while True:
    #     for message in queue.receive_messages():


if __name__ == "__main__":
    main()
    logger.info("{} Quitting Submission Worker.".format(WORKER_LOGS_PREFIX))
