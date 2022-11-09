import importlib
import subprocess
import traceback
import zipfile
import requests
import sys
import os
import tempfile
import logging
import shutil
import boto3
import botocore
import signal
import json
import time
import django
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'valhub.settings'

django.setup()

from analyses.models import Analysis
from jobs.models import Submission


# base
BASE_TEMP_DIR = tempfile.mkdtemp()  # "/tmp/tmpj6o45zwr"
COMPUTE_DIRECTORY_PATH = os.path.join(BASE_TEMP_DIR, "compute")
ANALYSIS_DATA_BASE_DIR = os.path.join(COMPUTE_DIRECTORY_PATH, "analysis_data")
SUBMISSION_DATA_BASE_DIR = os.path.join(
    COMPUTE_DIRECTORY_PATH, "submission_files")

# analysis
ANALYSIS_DATA_DIR = os.path.join(
    ANALYSIS_DATA_BASE_DIR, "analysis_{analysis_id}")
ANALYSIS_IMPORT_STRING = "analysis_data.analysis_{analysis_id}"
ANALYSIS_ANNOTATION_FILE_PATH = os.path.join(
    ANALYSIS_DATA_DIR, "{annotation_file}")
ANALYSIS_DATA_FILE_PATH = os.path.join(ANALYSIS_DATA_DIR, "{data_file}")

# submission
SUBMISSION_DATA_DIR = os.path.join(
    SUBMISSION_DATA_BASE_DIR, "submission_{submission_id}"
)
SUBMISSION_IMPORT_STRING = "submission_files.submission_{submission_id}"
SUBMISSION_INPUT_FILE_PATH = os.path.join(SUBMISSION_DATA_DIR, "{input_file}")

# log
WORKER_LOGS_PREFIX = "WORKER_LOG"
SUBMISSION_LOGS_PREFIX = "SUBMISSION_LOG"

EVALUATION_SCRIPTS = {}
SUBMISSION_ALGORITHMS = {}
ANNOTATION_FILE_NAME_MAP = {}

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

django.db.close_old_connections()


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


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


def delete_submission_data_directory(location):
    """
    Helper function to delete submission data from location `location`
    Arguments:
        location {[string]} -- Location of directory to be removed.
    """
    try:
        shutil.rmtree(location)
    except Exception as e:
        logger.exception(
            "{} Failed to delete submission data directory {}, error {}".format(
                WORKER_LOGS_PREFIX, location, e
            )
        )


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


############ analysis functions #############


def extract_analysis_data(analysis):
    analysis_data_directory = ANALYSIS_DATA_DIR.format(
        analysis_id=analysis.analysis_id
    )
    # create analysis directory as package
    create_dir_as_python_package(analysis_data_directory)

    # "https://github.com/slacgismo/pv-validation-hub/raw/mengdiz/examples/analysis_1.zip"
    # print(analysis.evaluation_script)
    # print(analysis.evaluation_script.url)
    evaluation_script_url = analysis.evaluation_script  # .url
    # evaluation_script_url = return_file_url_per_environment(
    #     evaluation_script_url
    # )

    # download and extract analysis with requirements.txt, evaluation_script, annotation_file, test_data
    analysis_zip_file = os.path.join(
        analysis_data_directory, "analysis_{}.zip".format(analysis.analysis_id)
    )
    download_and_extract_zip_file(
        evaluation_script_url, analysis_zip_file, ANALYSIS_DATA_BASE_DIR
    )

    annotation_file_name = analysis.annotation_file_name
    ANNOTATION_FILE_NAME_MAP[analysis.analysis_id] = annotation_file_name

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
        # analysis = Analysis()
        # analysis.analysis_id = 1
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


############ submission functions #############
def extract_submission_data(submission_id):
    """
    * Expects submission id and extracts input file for it.
    """

    try:
        submission = Submission.objects.get(submission_id=submission_id)
        # submission = Submission()
        # submission.submission_id = submission_id
    except Submission.DoesNotExist:
        logger.critical(
            "{} Submission {} does not exist".format(
                SUBMISSION_LOGS_PREFIX, submission_id
            )
        )
        traceback.print_exc()
        # return from here so that the message can be acked
        # This also indicates that we don't want to take action
        # for message corresponding to which submission entry
        # does not exist
        return None
    # Ignore submissions with status cancelled
    # if submission.status == Submission.CANCELLED:
    #     logger.info(
    #         "{} Submission {} was cancelled by the user".format(
    #             SUBMISSION_LOGS_PREFIX, submission_id
    #         )
    #     )
    #     return None

    submission_data_directory = SUBMISSION_DATA_DIR.format(
        submission_id=submission_id
    )
    # create submission directory
    create_dir_as_python_package(submission_data_directory)

    # download and extract submission with algorithm (predict function)
    # "https://github.com/slacgismo/pv-validation-hub/raw/mengdiz/examples/submission_1.zip"
    submission_algorithm_url = submission.algorithm  # .url
    submission_zip_file = os.path.join(
        submission_data_directory, "submission_{}.zip".format(submission_id)
    )
    download_and_extract_zip_file(
        submission_algorithm_url, submission_zip_file, SUBMISSION_DATA_BASE_DIR)

    # import as module
    importlib.invalidate_caches()
    submission_module = importlib.import_module(
        SUBMISSION_IMPORT_STRING.format(submission_id=1)
    )
    SUBMISSION_ALGORITHMS[submission_id] = submission_module

    return submission


def run_submission(analysis_id, submission, user_annotation_file_path):
    """
    * receives a analysis id and user annotation file path
    * checks whether the corresponding evaluation script for the analysis exists or not
    * checks the above for annotation file
    * calls evaluation script via subprocess passing annotation file and user_annotation_file_path as argument
    """
    # execute algorithm
    submission_id = submission.submission_id
    analysis_data_file_path = ANALYSIS_DATA_FILE_PATH.format(
        analysis_id=analysis_id, data_file='test_data')
    SUBMISSION_ALGORITHMS[submission_id].predict(analysis_data_file_path,
                                                 user_annotation_file_path)

    # ANNOTATION_FILE_NAME_MAP[analysis_id]
    annotation_file_name = "test_annotation.txt"
    annotation_file_path = ANALYSIS_ANNOTATION_FILE_PATH.format(
        analysis_id=analysis_id,
        annotation_file=annotation_file_name,
    )
    try:
        # importlib.invalidate_caches()
        # analysis_module = importlib.import_module(
        #     ANALYSIS_IMPORT_STRING.format(analysis_id=analysis_id)
        # )
        # EVALUATION_SCRIPTS[analysis_id] = analysis_module

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
                        "metric1":30,
                        "metric2":50,
                     }
                  }
               ],
               "submission_metadata": {'foo': 'bar'},
               "submission_result": ['foo', 'bar'],
            }
        """
        # submission_output["execution_time"] = 30
        print(submission_output)
    except Exception as e:
        print(e)


def process_submission_message(message):
    """
    Extracts the submission related metadata from the message
    and send the submission object for evaluation
    """
    analysis_id = message.get("analysis_pk")
    # phase_id = message.get("phase_pk")
    submission_id = message.get("submission_pk")
    submission_instance = extract_submission_data(submission_id)

    # so that the further execution does not happen
    if not submission_instance:
        return

    user_annotation_file_path = os.path.join(
        SUBMISSION_DATA_DIR.format(submission_id=submission_id),
        "test_pred.txt",
    )
    run_submission(
        analysis_id,
        submission_instance,
        user_annotation_file_path,
    )
    # Delete submission data after processing submission
    delete_submission_data_directory(
        SUBMISSION_DATA_DIR.format(submission_id=submission_id)
    )


def process_submission_callback(body):
    try:
        logger.info(
            "{} [x] Received submission message {}".format(
                SUBMISSION_LOGS_PREFIX, body
            )
        )
        # body = yaml.safe_load(body)
        # body = dict((k, int(v)) for k, v in body.items())
        body = json.loads(body)
        process_submission_message(body)
    except Exception as e:
        logger.exception(
            "{} Exception while receiving message from submission queue with error {}".format(
                SUBMISSION_LOGS_PREFIX, e
            )
        )


############ queue functions #############


def get_or_create_sqs_queue(queue_name):
    """
    Returns:
        Returns the SQS Queue object
    """
    sqs = boto3.resource(
        "sqs",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    )
    if queue_name == "":
        queue_name = "valhub_submission_queue"
    # Check if the queue exists. If no, then create one
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        if (
            ex.response["Error"]["Code"]
            != "AWS.SimpleQueueService.NonExistentQueue"
        ):
            logger.exception("Cannot get queue: {}".format(queue_name))
        queue = sqs.create_queue(QueueName=queue_name)
    return queue


def main():
    killer = GracefulKiller()
    logger.info(
        "{} Using {} as temp directory to store data".format(
            WORKER_LOGS_PREFIX, BASE_TEMP_DIR
        )
    )
    create_dir_as_python_package(COMPUTE_DIRECTORY_PATH)
    sys.path.append(COMPUTE_DIRECTORY_PATH)

    q_params = {}
    # q_params["end_date__gt"] = timezone.now()

    # primary key
    analysis_pk = 1  # os.environ.get("ANALYSIS_PK")
    if analysis_pk:
        q_params["pk"] = analysis_pk

    # load analysis
    maximum_concurrent_submissions, analysis = load_analysis_and_return_max_submissions(
        q_params)
    # print(maximum_concurrent_submissions)

    # create submission directory
    create_dir_as_python_package(SUBMISSION_DATA_BASE_DIR)

    # create message queue
    queue_name = os.environ.get(
        "CHALLENGE_QUEUE", "valhub_submission_queue.fifo")
    queue = get_or_create_sqs_queue(queue_name)
    # print(queue)

    # infinite loop to listen and process messages
    while True:
        for message in queue.receive_messages():
            logger.info(
                "{} Processing message body: {}".format(
                    WORKER_LOGS_PREFIX, message.body
                )
            )
            print(message.body)
            process_submission_callback(message.body)
            # Let the queue know that the message is processed
            message.delete()

        if killer.kill_now:
            break
        time.sleep(0.1)


if __name__ == "__main__":
    main()
    logger.info("{} Quitting Submission Worker.".format(WORKER_LOGS_PREFIX))
