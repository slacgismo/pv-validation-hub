from importlib import import_module
import traceback
from typing import Any
import zipfile
import requests
import sys
import os
import tempfile
import logging.config
import logging.handlers
import shutil
import boto3
import botocore.exceptions
import signal
import json
import time
import urllib.request
import inspect
import threading
import time


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return "PROD" not in os.environ


is_s3_emulation = is_local()

S3_BUCKET_NAME = "pv-validation-hub-bucket"

if is_s3_emulation:
    api_base_url = "api:8005"
else:
    api_base_url = "api.pv-validation-hub.org"

SUBMITTING = "submitting"
SUBMITTED = "submitted"
RUNNING = "running"
FAILED = "failed"
FINISHED = "finished"

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


def setup_logging():
    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logging_config.json"
    )

    with open(config_file_path, "r") as f:
        config: dict[str, Any] = json.load(f)

    logging.config.dictConfig(config)


setup_logging()


class WorkerException(Exception):
    pass


class RunnerException(Exception):
    pass


def pull_from_s3(s3_file_path: str):
    logger.info(f"pull file {s3_file_path} from s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if is_s3_emulation:
        s3_file_full_path = "http://s3:5000/get_object/" + s3_file_path
        # s3_file_full_path = 'http://localhost:5000/get_object/' + s3_file_path
    else:
        s3_file_full_path = "s3://" + s3_file_path

    target_file_path = os.path.join("/tmp/", s3_file_full_path.split("/")[-1])

    if is_s3_emulation:
        r = requests.get(s3_file_full_path, stream=True)
        if r.status_code != 200:
            print(
                f"error get file {s3_file_path} from s3, status code {r.status_code} {r.content}",
                file=sys.stderr,
            )
        with open(target_file_path, "wb") as f:
            f.write(r.content)
    else:
        s3 = boto3.client("s3")

        try:
            s3.download_file(S3_BUCKET_NAME, s3_file_path, target_file_path)
        except:
            raise FileNotFoundError(f"File {target_file_path} not found in s3 bucket.")

    return target_file_path


def push_to_s3(local_file_path, s3_file_path):
    logger.info(f"push file {local_file_path} to s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if is_s3_emulation:
        s3_file_full_path = "http://s3:5000/put_object/" + s3_file_path
    else:
        s3_file_full_path = "s3://" + s3_file_path

    if is_s3_emulation:
        with open(local_file_path, "rb") as f:
            file_content = f.read()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                print(
                    f"error put file {s3_file_path} to s3, status code {r.status_code} {r.content}",
                    file=sys.stderr,
                )
    else:

        s3 = boto3.client("s3")

        try:
            s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_path)
        except:
            return None


def list_s3_bucket(s3_dir):
    logger.info(f"list s3 bucket {s3_dir}")
    if s3_dir.startswith("/"):
        s3_dir = s3_dir[1:]

    if is_s3_emulation:
        s3_dir_full_path = "http://s3:5000/list_bucket/" + s3_dir
        # s3_dir_full_path = 'http://localhost:5000/list_bucket/' + s3_dir
    else:
        s3_dir_full_path = "s3://" + s3_dir

    all_files = []
    if is_s3_emulation:
        r = requests.get(s3_dir_full_path)
        ret = r.json()
        for entry in ret["Contents"]:
            all_files.append(os.path.join(s3_dir.split("/")[0], entry["Key"]))
    else:
        # check s3_dir string to see if it contains "pv-validation-hub-bucket/"
        # if so, remove it
        s3_dir = s3_dir.replace("pv-validation-hub-bucket/", "")
        logger.info(f"dir after removing pv-validation-hub-bucket/ returns {s3_dir}")

        s3 = boto3.client("s3")
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=s3_dir)
        for page in pages:
            if page["KeyCount"] > 0:
                for entry in page["Contents"]:
                    if "Key" in entry:
                        all_files.append(entry["Key"])

        # remove the first entry if it is the same as s3_dir
        if len(all_files) > 0 and all_files[0] == s3_dir:
            all_files.pop(0)

    logger.info(f"listed s3 bucket {s3_dir_full_path} returns {all_files}")
    return all_files


def update_submission_status(analysis_id, submission_id, new_status):
    # route needs to be a string stored in a variable, cannot parse in deployed environment
    api_route = f"http://{api_base_url}/submissions/analysis/{analysis_id}/change_submission_status/{submission_id}"
    r = requests.put(api_route, data={"status": new_status})
    if r.status_code != 200:
        print(
            f"error update submission status to {new_status}, status code {r.status_code} {r.content}",
            file=sys.stderr,
        )


def update_submission_result(analysis_id, submission_id, result_json):
    headers = {"Content-Type": "application/json"}
    api_route = f"http://{api_base_url}/submissions/analysis/{analysis_id}/update_submission_result/{submission_id}"
    r = requests.put(api_route, json=result_json, headers=headers)
    if r.status_code != 200:
        print(
            f"error update submission result to {result_json}, status code {r.status_code} {r.content}",
            file=sys.stderr,
        )


SUBMITTING = "submitting"
SUBMITTED = "submitted"
RUNNING = "running"
FAILED = "failed"
FINISHED = "finished"

# base
BASE_TEMP_DIR = tempfile.mkdtemp()  # "/tmp/tmpj6o45zwr"
COMPUTE_DIRECTORY_PATH = os.path.join(BASE_TEMP_DIR, "compute")
ANALYSIS_DATA_BASE_DIR = os.path.join(COMPUTE_DIRECTORY_PATH, "analysis_data")
SUBMISSION_DATA_BASE_DIR = os.path.join(COMPUTE_DIRECTORY_PATH, "submission_files")

# analysis
ANALYSIS_DATA_DIR = os.path.join(ANALYSIS_DATA_BASE_DIR, "analysis_{analysis_id}")
ANALYSIS_IMPORT_STRING = "analysis_data.analysis_{analysis_id}"
ANALYSIS_ANNOTATION_FILE_PATH = os.path.join(ANALYSIS_DATA_DIR, "{annotation_file}")
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

# AWS
S3_BUCKET_NAME = "pv-validation-hub-bucket"

EVALUATION_SCRIPTS = {}
SUBMISSION_ALGORITHMS = {}
ANNOTATION_FILE_NAME_MAP = {}


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info(f"Set signal to exit gracefully")
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


def extract_zip_file(download_location, extract_location, new_name=None):
    """
    Helper function to extract zip file
    Params:
        * `download_location`: Location of zip file
        * `extract_location`: Location of directory for extracted file
    """
    zip_ref = zipfile.ZipFile(download_location, "r")
    original_name = zip_ref.namelist()[0]
    zip_ref.extractall(extract_location)
    zip_ref.close()

    # print("extract_location: {}".format(extract_location))

    if new_name is not None:
        source_dir = os.path.join(extract_location, original_name)
        target_dir = os.path.join(extract_location, new_name)
        for file_name in os.listdir(source_dir):
            shutil.move(
                os.path.join(source_dir, file_name), os.path.join(target_dir, file_name)
            )


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


def download_and_extract_zip_file(
    file_name, download_location, extract_location, new_name=None
):
    """
    * Function to extract download a zip file, extract it and then removes the zip file.
    * `download_location` should include name of file as well.
    """
    try:
        s3 = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
        )
        s3.download_file(S3_BUCKET_NAME, file_name, download_location)
    except Exception as e:
        logger.error(
            "{} Failed to fetch file from {}, error {}".format(
                WORKER_LOGS_PREFIX, file_name, e
            )
        )

    # extract zip file
    extract_zip_file(download_location, extract_location, new_name)

    # delete zip file
    delete_zip_file(download_location)


############ analysis functions #############


def extract_analysis_data(analysis_id, current_evaluation_dir):

    # download evaluation scripts and requirements.txt etc.
    files = list_s3_bucket(
        f"pv-validation-hub-bucket/evaluation_scripts/{analysis_id}/"
    )
    logger.info(f"pull evaluation scripts from s3")
    for file in files:
        logger.info(f"pull file {file} from s3")
        tmp_path = pull_from_s3(file)
        shutil.move(
            tmp_path, os.path.join(current_evaluation_dir, tmp_path.split("/")[-1])
        )
    # create data directory and sub directories
    data_dir = os.path.join(current_evaluation_dir, "data")
    file_data_dir = os.path.join(data_dir, "file_data")
    validation_data_dir = os.path.join(data_dir, "validation_data")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(file_data_dir, exist_ok=True)
    os.makedirs(validation_data_dir, exist_ok=True)
    # # move file_test_link
    # shutil.move(os.path.join(current_evaluation_dir, 'file_test_link.csv'),
    #             os.path.join(data_dir, 'file_test_link.csv'))
    # shutil.move(os.path.join(current_evaluation_dir, 'config.json'),
    #             os.path.join(data_dir, 'config.json'))
    # download data files
    analyticals = list_s3_bucket(f"pv-validation-hub-bucket/data_files/analytical/")
    for analytical in analyticals:
        tmp_path = pull_from_s3(analytical)
        shutil.move(tmp_path, os.path.join(file_data_dir, tmp_path.split("/")[-1]))
    ground_truths = list_s3_bucket(f"pv-validation-hub-bucket/data_files/ground_truth/")
    for ground_truth in ground_truths:
        tmp_path = pull_from_s3(ground_truth)
        shutil.move(
            tmp_path, os.path.join(validation_data_dir, tmp_path.split("/")[-1])
        )


def create_current_evaluation_dir(dir_name="current_evaluation"):
    local_dir = dir_name
    logger.info(f"create local folder {local_dir}")
    current_evaluation_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), local_dir
    )
    logger.info(f"local folder located at {current_evaluation_dir}")
    if not os.path.exists(current_evaluation_dir):
        os.makedirs(current_evaluation_dir)
        logger.info(f"created local folder {current_evaluation_dir}")
    return current_evaluation_dir


def load_analysis(analysis_id, current_evaluation_dir):

    logger.info("pull and extract analysis")
    extract_analysis_data(analysis_id, current_evaluation_dir)

    # Copy the validation runner into the current evaluation directory
    shutil.copy(
        os.path.join("/root/worker", "pvinsight-validation-runner.py"),
        os.path.join(current_evaluation_dir, "pvinsight-validation-runner.py"),
    )

    # import analysis runner as a module
    sys.path.insert(0, current_evaluation_dir)
    runner_module_name = "pvinsight-validation-runner"
    logger.info(f"import runner module {runner_module_name}")
    analysis_module = import_module(runner_module_name)
    sys.path.pop(0)

    analysis_function = getattr(analysis_module, "run")
    function_parameters = list(inspect.signature(analysis_function).parameters)
    logger.info(f"analysis function parameters: {function_parameters}")
    return analysis_function, function_parameters


############ submission functions #############


def process_submission_message(message: dict[str, Any]):
    """
    Extracts the submission related metadata from the message
    and send the submission object for evaluation
    """
    analysis_id = int(message.get("analysis_pk", None))
    submission_id = int(message.get("submission_pk", None))
    user_id = int(message.get("user_pk", None))
    submission_filename = message.get("submission_filename", None)

    if not analysis_id or not submission_id or not user_id or not submission_filename:
        logger.error(
            "{} Missing required fields in submission message {}".format(
                SUBMISSION_LOGS_PREFIX, message
            )
        )
        return

    current_evaluation_dir = create_current_evaluation_dir()

    analysis_function, function_parameters = load_analysis(
        analysis_id, current_evaluation_dir
    )
    logger.info(f"function parameters returns {function_parameters}")

    # execute the runner script
    # assume ret indicates the directory of result of the runner script
    argument = f"submission_files/submission_user_{user_id}/submission_{submission_id}/{submission_filename}"
    logger.info(f"execute runner module function with argument {argument}")

    # argument is the s3 file path. All pull from s3 calls CANNOT use the bucket name in the path.
    # bucket name must be passed seperately to boto3 calls.
    ret = analysis_function(argument, current_evaluation_dir)
    logger.info(f"runner module function returns {ret}")

    logger.info(f"update submission status to {FINISHED}")
    update_submission_status(analysis_id, submission_id, FINISHED)

    # Uploads public metrics to DB, ret expected format {'module': 'pvanalytics-cpd-module', 'mean_mean_absolute_error': 2.89657870134743, 'mean_run_time': 24.848265788458676, 'data_requirements': ['time_series', 'latitude', 'longitude', 'data_sampling_frequency']}
    res_json = ret
    logger.info(f"update submission result to {res_json}")
    update_submission_result(analysis_id, submission_id, res_json)

    logger.info(f"upload result files to s3")

    res_files_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "current_evaluation/results"
    )
    for dir_path, dir_names, file_names in os.walk(res_files_path):
        for file_name in file_names:
            full_file_name = os.path.join(dir_path, file_name)
            relative_file_name = full_file_name[len(f"{res_files_path}/") :]

            if is_s3_emulation:
                s3_full_path = f"pv-validation-hub-bucket/submission_files/submission_user_{user_id}/submission_{submission_id}/results/{relative_file_name}"
            else:
                s3_full_path = f"submission_files/submission_user_{user_id}/submission_{submission_id}/results/{relative_file_name}"

            logger.info(
                f'upload result file "{full_file_name}" to s3 path "{s3_full_path}"'
            )
            push_to_s3(full_file_name, s3_full_path)

    # remove the current evaluation dir
    logger.info(f"remove directory {current_evaluation_dir}")
    shutil.rmtree(current_evaluation_dir)


def process_submission_callback(body: str):
    logger.info(
        "{} [x] Received submission message {}".format(SUBMISSION_LOGS_PREFIX, body)
    )
    # body = yaml.safe_load(body)
    # body = dict((k, int(v)) for k, v in body.items())
    json_message: dict[str, Any] = json.loads(body)
    process_submission_message(json_message)


############ queue functions #############


def get_or_create_sqs_queue(queue_name):
    """
    Returns:
        Returns the SQS Queue object
    """
    # Use the Docker endpoint URL for local development
    if is_s3_emulation:
        sqs = boto3.resource(
            "sqs",
            endpoint_url="http://sqs:9324",
            region_name="elasticmq",
            aws_secret_access_key="x",
            aws_access_key_id="x",
            use_ssl=False,
        )
    # Use the production AWS environment for other environments
    else:
        sqs = boto3.resource(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
        )

    if queue_name == "":
        queue_name = "valhub_submission_queue.fifo"
    # Check if the queue exists. If no, then create one
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        if (
            ex.response.get("Error", {}).get("Code")
            != "AWS.SimpleQueueService.NonExistentQueue"
        ):
            logger.exception("Cannot get queue: {}".format(queue_name))
        queue = sqs.create_queue(QueueName=queue_name, Attributes={"FifoQueue": "true"})

    return queue


def get_analysis_pk():
    instance_id = (
        urllib.request.urlopen("http://169.254.169.254/latest/meta-data/instance-id")
        .read()
        .decode()
    )

    ec2_resource = boto3.resource(
        "ec2",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
    )
    ec2_instance = ec2_resource.Instance(instance_id)
    tags = ec2_instance.tags
    for tag in tags:
        if tag["Key"] == "ANALYSIS_PK":
            return int(tag["Value"])
    return 1


# function to update visibility timeout, to prevent the error "ReceiptHandle is invalid. Reason: The receipt handle has expired."
def update_visibility_timeout(queue, message, timeout, event: threading.Event):
    # Use the Docker endpoint URL for local development
    if is_s3_emulation:
        sqs = boto3.client(
            "sqs",
            endpoint_url="http://sqs:9324",
            region_name="elasticmq",
            aws_secret_access_key="x",
            aws_access_key_id="x",
            use_ssl=False,
        )
    # Use the production AWS environment for other environments
    else:
        sqs = boto3.client(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
        )

    while True:
        # Update visibility timeout
        sqs.change_message_visibility(
            QueueUrl=queue.url,
            ReceiptHandle=message.receipt_handle,
            VisibilityTimeout=timeout,
        )
        time.sleep(60)  # Adjust the sleep duration as needed
        if event.is_set():
            break


def handle_error(message, error_code, error_message):
    # update submission status to failed
    body = json.loads(message.body)
    analysis_id = int(body.get("analysis_pk"))
    submission_id = int(body.get("submission_pk"))
    update_submission_status(analysis_id, submission_id, FAILED)

    # Send the error message to the submission


def main():
    # killer = GracefulKiller()
    logger.info(
        "{} Using {} as temp directory to store data".format(
            WORKER_LOGS_PREFIX, BASE_TEMP_DIR
        )
    )
    queue = get_or_create_sqs_queue("valhub_submission_queue.fifo")
    # print(queue)

    is_finished = False

    # infinite loop to listen and process messages
    while not is_finished:
        messages = queue.receive_messages(
            MaxNumberOfMessages=1, VisibilityTimeout=43200
        )

        for message in messages:
            logger.info(
                "{} Processing message body: {}".format(
                    WORKER_LOGS_PREFIX, message.body
                )
            )
            logger.info(f"Message body: {message.body}")

            # start a thread to refresh the timeout
            stop_event = threading.Event()
            t = threading.Thread(
                target=update_visibility_timeout,
                args=(queue, message, 43200, stop_event),
            )
            t.start()
            try:
                logger.info(f"Message body type: {type(message.body)}")
                process_submission_callback(message.body)
            except WorkerException as e:
                error_code = e.args[0]
                error_message = e.args[1]
                logger.error(
                    "{} WorkerException while processing message from submission queue with error code {} and message {}".format(
                        WORKER_LOGS_PREFIX, error_code, error_message
                    )
                )
            except RunnerException as e:
                error_code = e.args[0]
                error_message = e.args[1]
                logger.error(
                    "{} RunnerException while processing message from submission queue with error code {} and message {}".format(
                        WORKER_LOGS_PREFIX, error_code, error_message
                    )
                )

            except Exception as e:
                logger.exception(
                    "{} Exception while processing message from submission queue with error {}".format(
                        WORKER_LOGS_PREFIX, e
                    )
                )
                # # update submission status to failed
                # body = json.loads(message.body)
                # analysis_id = int(body.get("analysis_pk"))
                # submission_id = int(body.get("submission_pk"))
                # update_submission_status(analysis_id, submission_id, FAILED)
            finally:
                message.delete()
                # Let the queue know that the message is processed
                logger.info(
                    "{} Message processed successfully".format(WORKER_LOGS_PREFIX)
                )
                stop_event.set()
                t.join()

            is_finished = True
            break

        # if killer.kill_now:
        #     break
        time.sleep(0.1)


if __name__ == "__main__":
    logger.info("{} Starting Submission Worker.".format(WORKER_LOGS_PREFIX))
    main()
    logger.info("{} Quitting Submission Worker.".format(WORKER_LOGS_PREFIX))
