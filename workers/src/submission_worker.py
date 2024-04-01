from importlib import import_module
from typing import Any, Callable, Optional
import requests
import sys
import os
import tempfile
import logging.config
import logging.handlers
import shutil
import boto3
import botocore.exceptions
import json
import time
import urllib.request
import inspect
import threading
import pandas as pd
from logger import setup_logging
from utility import timing, is_local


setup_logging()

logger = logging.getLogger(__name__)

IS_LOCAL = is_local()

S3_BUCKET_NAME = "pv-validation-hub-bucket"

API_BASE_URL = "api:8005" if IS_LOCAL else "api.pv-validation-hub.org"

SUBMITTING = "submitting"
SUBMITTED = "submitted"
RUNNING = "running"
FAILED = "failed"
FINISHED = "finished"


# base
BASE_TEMP_DIR = tempfile.mkdtemp()  # "/tmp/tmpj6o45zwr"
# Set to folder where the evaluation scripts are stored


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, "..", "logs"))
CURRENT_EVALUATION_DIR = os.path.abspath(
    os.path.join(FILE_DIR, "..", "current_evaluation")
)

# log
WORKER_LOGS_PREFIX = "WORKER_LOG"
SUBMISSION_LOGS_PREFIX = "SUBMISSION_LOG"


class WorkerException(Exception):
    pass


class RunnerException(Exception):
    pass


def pull_from_s3(s3_file_path: str):
    logger.info(f"pull file {s3_file_path} from s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        s3_file_full_path = "http://s3:5000/get_object/" + s3_file_path
        # s3_file_full_path = 'http://localhost:5000/get_object/' + s3_file_path
    else:
        s3_file_full_path = "s3://" + s3_file_path

    target_file_path = os.path.join("/tmp/", s3_file_full_path.split("/")[-1])

    if IS_LOCAL:
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
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error: {e}")
            raise FileNotFoundError(
                f"File {target_file_path} not found in s3 bucket."
            )

    return target_file_path


def push_to_s3(local_file_path, s3_file_path):
    logger.info(f"push file {local_file_path} to s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        s3_file_full_path = (
            f"http://s3:5000/put_object/{S3_BUCKET_NAME}/" + s3_file_path
        )
    else:
        s3_file_full_path = "s3://" + s3_file_path

    if IS_LOCAL:
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
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error: {e}")
            return None


def list_s3_bucket(s3_dir: str):
    logger.info(f"list s3 bucket {s3_dir}")
    if s3_dir.startswith("/"):
        s3_dir = s3_dir[1:]

    if IS_LOCAL:
        s3_dir_full_path = "http://s3:5000/list_bucket/" + s3_dir
        # s3_dir_full_path = 'http://localhost:5000/list_bucket/' + s3_dir
    else:
        s3_dir_full_path = "s3://" + s3_dir

    all_files: list[str] = []
    if IS_LOCAL:
        r = requests.get(s3_dir_full_path)
        ret = r.json()
        for entry in ret["Contents"]:
            all_files.append(os.path.join(s3_dir.split("/")[0], entry["Key"]))
    else:
        # check s3_dir string to see if it contains "pv-validation-hub-bucket/"
        # if so, remove it
        s3_dir = s3_dir.replace("pv-validation-hub-bucket/", "")
        logger.info(
            f"dir after removing pv-validation-hub-bucket/ returns {s3_dir}"
        )

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
    api_route = f"http://{API_BASE_URL}/submissions/analysis/{analysis_id}/change_submission_status/{submission_id}"
    r = requests.put(api_route, data={"status": new_status})
    if r.status_code != 200:
        print(
            f"error update submission status to {new_status}, status code {r.status_code} {r.content}",
            file=sys.stderr,
        )


def update_submission_result(analysis_id, submission_id, result_json):
    headers = {"Content-Type": "application/json"}
    api_route = f"http://{API_BASE_URL}/submissions/analysis/{analysis_id}/update_submission_result/{submission_id}"
    r = requests.put(api_route, json=result_json, headers=headers)
    if r.status_code != 200:
        print(
            f"error update submission result to {result_json}, status code {r.status_code} {r.content}",
            file=sys.stderr,
        )


def extract_analysis_data(  # noqa: C901
    analysis_id: str, current_evaluation_dir: str
) -> pd.DataFrame:

    # download evaluation scripts and requirements.txt etc.
    files = list_s3_bucket(
        f"pv-validation-hub-bucket/evaluation_scripts/{analysis_id}/"
    )
    # check if required files exist
    if len(files) == 0:
        raise FileNotFoundError(
            f"No files found in s3 bucket for analysis {analysis_id}"
        )

    required_files = [
        "config.json",
        "file_test_link.csv",
    ]
    file_names = [file.split("/")[-1] for file in files]

    for required_file in required_files:
        if required_file not in file_names:
            raise FileNotFoundError(
                f"Required file {required_file} not found in s3 bucket for analysis {analysis_id}"
            )

    logger.info("pull evaluation scripts from s3")
    for file in files:
        logger.info(f"pull file {file} from s3")
        tmp_path = pull_from_s3(file)
        shutil.move(
            tmp_path,
            os.path.join(current_evaluation_dir, tmp_path.split("/")[-1]),
        )

    # create data directory and sub directories
    data_dir = os.path.join(current_evaluation_dir, "data")
    file_data_dir = os.path.join(data_dir, "file_data")
    validation_data_dir = os.path.join(data_dir, "validation_data")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(file_data_dir, exist_ok=True)
    os.makedirs(validation_data_dir, exist_ok=True)

    # File category link: This file represents the file_category_link table,
    # which links specific files in the file_metadata table.
    # This table exists specifically to allow for
    # many-to-many relationships, where one file can link to multiple
    # categories/tests, and multiple categories/tests can link to multiple
    # files.
    file_test_link = pd.read_csv(
        os.path.join(current_evaluation_dir, "file_test_link.csv")
    )

    # Get the unique file ids
    unique_file_ids = file_test_link["file_id"].unique()

    # File metadata: This file represents the file_metadata table, which is
    # the master table for files associated with different tests (az-tilt,
    # time shifts, degradation, etc.). Contains file name, associated file
    # information (sampling frequency, specific test, timezone, etc) as well
    # as ground truth information to test against in the validation_dictionary
    # field
    # For each unique file id, make a GET request to the Django API to get the corresponding file metadata
    file_metadata_list: list[dict[str, Any]] = []
    for file_id in unique_file_ids:
        fmd_url = (
            f"http://{API_BASE_URL}/file_metadata/filemetadata/{file_id}/"
        )
        response = requests.get(fmd_url)
        if not response.ok:
            raise FileNotFoundError(
                f"File metadata for file id {file_id} not found in Django API"
            )
        file_metadata_list.append(response.json())

    # Convert the list of file metadata to a DataFrame
    file_metadata_df = pd.DataFrame(file_metadata_list)

    if file_metadata_df.empty:
        raise FileNotFoundError(
            f"No file metadata found in Django API for analysis {analysis_id}"
        )

    files_for_analysis: list[str] = file_metadata_df["file_name"].tolist()

    analyticals = list_s3_bucket(
        f"pv-validation-hub-bucket/data_files/analytical/"
    )
    analytical_files = [
        analytical.split("/")[-1] for analytical in analyticals
    ]
    ground_truths = list_s3_bucket(
        f"pv-validation-hub-bucket/data_files/ground_truth/{analysis_id}/"
    )
    ground_truth_files = [
        ground_truth.split("/")[-1] for ground_truth in ground_truths
    ]

    if not all(file in ground_truth_files for file in files_for_analysis):
        raise FileNotFoundError(
            f"Ground truth data files not found for analysis {analysis_id}"
        )

    if not all(file in analytical_files for file in files_for_analysis):
        raise FileNotFoundError(
            f"Analytical data files not found for analysis {analysis_id}"
        )

    for file in files_for_analysis:

        analytical = analyticals[analytical_files.index(file)]

        tmp_path = pull_from_s3(analytical)
        shutil.move(
            tmp_path, os.path.join(file_data_dir, tmp_path.split("/")[-1])
        )

        ground_truth = ground_truths[ground_truth_files.index(file)]

        tmp_path = pull_from_s3(ground_truth)
        shutil.move(
            tmp_path,
            os.path.join(validation_data_dir, tmp_path.split("/")[-1]),
        )

    return file_metadata_df


def create_current_evaluation_dir(directory_path: str):
    current_evaluation_dir = directory_path

    if os.path.exists(current_evaluation_dir):
        logger.info(f"remove directory {current_evaluation_dir}")
        shutil.rmtree(current_evaluation_dir, ignore_errors=True)

    os.makedirs(current_evaluation_dir, exist_ok=True)
    logger.info(f"created evaluation folder {current_evaluation_dir}")
    return current_evaluation_dir


def load_analysis(analysis_id: str, current_evaluation_dir: str) -> tuple[
    Callable[
        [str, pd.DataFrame, Optional[str], Optional[str]], dict[str, Any]
    ],
    list,
    pd.DataFrame,
]:

    logger.info("pull and extract analysis")
    file_metadata_df = extract_analysis_data(
        analysis_id, current_evaluation_dir
    )

    # Copy the validation runner into the current evaluation directory
    shutil.copy(
        os.path.join("/root/worker/src", "pvinsight-validation-runner.py"),
        os.path.join(current_evaluation_dir, "pvinsight-validation-runner.py"),
    )

    # import analysis runner as a module
    sys.path.insert(0, current_evaluation_dir)
    runner_module_name = "pvinsight-validation-runner"
    logger.info(f"import runner module {runner_module_name}")

    analysis_module = import_module(runner_module_name)

    sys.path.pop(0)

    try:
        analysis_function = getattr(analysis_module, "run")
        function_parameters = list(
            inspect.signature(analysis_function).parameters
        )
        logger.info(f"analysis function parameters: {function_parameters}")
    except AttributeError:
        logger.error(
            f"Runner module {runner_module_name} does not have a 'run' function"
        )
        raise WorkerException(
            1, "Runner module does not have a 'run' function"
        )
    return analysis_function, function_parameters, file_metadata_df


def process_submission_message(
    analysis_id: str,
    submission_id: str,
    user_id: str,
    submission_filename: str,
):
    """
    Extracts the submission related metadata from the message
    and send the submission object for evaluation
    """

    current_evaluation_dir = create_current_evaluation_dir(
        CURRENT_EVALUATION_DIR
    )

    analysis_function, function_parameters, file_metadata_df = load_analysis(
        analysis_id, current_evaluation_dir
    )
    logger.info(f"function parameters returns {function_parameters}")

    # execute the runner script
    # assume ret indicates the directory of result of the runner script
    argument = f"submission_files/submission_user_{user_id}/submission_{submission_id}/{submission_filename}"
    logger.info(f"execute runner module function with argument {argument}")

    # argument is the s3 file path. All pull from s3 calls CANNOT use the bucket name in the path.
    # bucket name must be passed seperately to boto3 calls.
    ret = analysis_function(
        argument, file_metadata_df, current_evaluation_dir, BASE_TEMP_DIR
    )
    logger.info(f"runner module function returns {ret}")

    logger.info(f"update submission status to {FINISHED}")
    update_submission_status(analysis_id, submission_id, FINISHED)

    # Uploads public metrics to DB, ret expected format {'module': 'pvanalytics-cpd-module', 'mean_mean_absolute_error': 2.89657870134743, 'mean_run_time': 24.848265788458676, 'data_requirements': ['time_series', 'latitude', 'longitude', 'data_sampling_frequency']}
    res_json = ret
    logger.info(f"update submission result to {res_json}")
    update_submission_result(analysis_id, submission_id, res_json)

    logger.info(f"upload result files to s3")

    res_files_path = os.path.join(
        CURRENT_EVALUATION_DIR,
        "results",
    )
    for dir_path, dir_names, file_names in os.walk(res_files_path):
        for file_name in file_names:
            full_file_name = os.path.join(dir_path, file_name)
            relative_file_name = full_file_name[len(f"{res_files_path}/") :]

            logger.info(f"full file name {full_file_name}")
            logger.info(f"relative file name {relative_file_name}")

            s3_full_path = f"submission_files/submission_user_{user_id}/submission_{submission_id}/results/{relative_file_name}"

            logger.info(
                f'upload result file "{full_file_name}" to s3 path "{s3_full_path}"'
            )
            push_to_s3(full_file_name, s3_full_path)

    # # remove the current evaluation dir
    # logger.info(f"remove directory {current_evaluation_dir}")
    # shutil.rmtree(current_evaluation_dir)


def get_or_create_sqs_queue(queue_name):
    """
    Returns:
        Returns the SQS Queue object
    """
    # Use the Docker endpoint URL for local development
    if IS_LOCAL:
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
        queue = sqs.create_queue(
            QueueName=queue_name, Attributes={"FifoQueue": "true"}
        )

    return queue


def get_analysis_pk():
    instance_id = (
        urllib.request.urlopen(
            "http://169.254.169.254/latest/meta-data/instance-id"
        )
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


def get_aws_sqs_client():
    if IS_LOCAL:
        sqs = boto3.client(
            "sqs",
            endpoint_url="http://sqs:9324",
            region_name="elasticmq",
            aws_secret_access_key="x",
            aws_access_key_id="x",
            use_ssl=False,
        )
        logger.info(f"Using local SQS endpoint")
    else:
        sqs = boto3.client(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
        )
        logger.info(f"Using AWS SQS endpoint")
    logger.debug(f"SQS type: {type(sqs)}")
    return sqs


# function to update visibility timeout, to prevent the error "ReceiptHandle is invalid. Reason: The receipt handle has expired."
def update_visibility_timeout(queue, message, timeout, event: threading.Event):
    # Use the Docker endpoint URL for local development
    sqs = get_aws_sqs_client()
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


@timing(verbose=True, logger=logger)
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

            json_message: dict[str, Any] = json.loads(message.body)

            analysis_id: str | None = json_message.get("analysis_pk", None)
            submission_id: str | None = json_message.get("submission_pk", None)
            user_id: str | None = json_message.get("user_pk", None)
            submission_filename: str | None = json_message.get(
                "submission_filename", None
            )

            if (
                not analysis_id
                or not submission_id
                or not user_id
                or not submission_filename
            ):
                logger.error(
                    "{} Missing required fields in submission message {}".format(
                        SUBMISSION_LOGS_PREFIX, json_message
                    )
                )
                raise ValueError(
                    1, "Missing required fields in submission message"
                )

            # start a thread to refresh the timeout
            stop_event = threading.Event()
            t = threading.Thread(
                target=update_visibility_timeout,
                args=(queue, message, 43200, stop_event),
            )
            t.start()

            try:
                process_submission_message(
                    analysis_id, submission_id, user_id, submission_filename
                )
            except Exception as e:
                try:
                    error_code = e.args[0]
                    error_message = e.args[1]
                except IndexError:
                    error_code = 1
                    error_message = str(e)

                logger.error(
                    f'Error processing message from submission queue with error code {error_code} and message "{error_message}"'
                )
                logger.exception(e)

            finally:
                message.delete()
                # Let the queue know that the message is processed
                logger.info(
                    "{} Message processed successfully".format(
                        WORKER_LOGS_PREFIX
                    )
                )
                stop_event.set()
                t.join()

            # rename log file to include submission_id

            log_file = os.path.join(LOG_FILE_DIR, "submission.log")
            json_log_file = os.path.join(LOG_FILE_DIR, "submission.log.jsonl")

            # push log files to s3

            push_to_s3(
                log_file,
                f"submission_files/submission_user_{user_id}/submission_{submission_id}/logs/submission.log",
            )
            push_to_s3(
                json_log_file,
                f"submission_files/submission_user_{user_id}/submission_{submission_id}/logs/submission.log.jsonl",
            )

            # Remove all log files
            os.remove(log_file)
            os.remove(json_log_file)

            is_finished = True
            break

        # if killer.kill_now:
        #     break
        time.sleep(0.1)


if __name__ == "__main__":
    logger.info("{} Starting Submission Worker.".format(WORKER_LOGS_PREFIX))
    _, execution_time = main()
    logger.info(f"Evaluation Worker took {execution_time:.3f} seconds to run")
    logger.info("{} Quitting Submission Worker.".format(WORKER_LOGS_PREFIX))