from importlib import import_module
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
import urllib.request
import inspect

def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return 'AWS_EXECUTION_ENV' not in os.environ and 'ECS_CONTAINER_METADATA_URI' not in os.environ and 'ECS_CONTAINER_METADATA_URI_V4' not in os.environ and 'PROD' not in os.environ

is_s3_emulation = is_local()

S3_BUCKET_NAME = "pv-validation-hub-bucket"


SUBMITTING = "submitting"
SUBMITTED = "submitted"
RUNNING = "running"
FAILED = "failed"
FINISHED = "finished"

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def pull_from_s3(s3_file_path):
    logger.info(f'pull file {s3_file_path} from s3')
    if s3_file_path.startswith('/'):
        s3_file_path = s3_file_path[1:]

    if is_s3_emulation:
        s3_file_full_path = 'http://s3:5000/get_object/' + s3_file_path
        # s3_file_full_path = 'http://localhost:5000/get_object/' + s3_file_path
    else:
        s3_file_full_path = 's3://' + s3_file_path
    
    target_file_path = os.path.join('/tmp/', s3_file_full_path.split('/')[-1])

    if is_s3_emulation:
        r = requests.get(s3_file_full_path, stream=True)
        if r.status_code != 200:
            print(f"error get file {s3_file_path} from s3, status code {r.status_code} {r.content}", file=sys.stderr)
        with open(target_file_path, "wb") as f:
            f.write(r.content)
    else:
        s3 = boto3.client('s3')

        try:
            s3.download_file(S3_BUCKET_NAME, s3_file_path, target_file_path)
        except:
            return None

    return target_file_path


def push_to_s3(local_file_path, s3_file_path):
    logger.info(f'push file {local_file_path} to s3')
    if s3_file_path.startswith('/'):
        s3_file_path = s3_file_path[1:]

    if is_s3_emulation:
        s3_file_full_path = 'http://s3:5000/put_object/' + s3_file_path
    else:
        s3_file_full_path = 's3://' + s3_file_path
    
    if is_s3_emulation:
        with open(local_file_path, "rb") as f:
            file_content = f.read()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                print(f"error put file {s3_file_path} to s3, status code {r.status_code} {r.content}", file=sys.stderr)
    else:

        s3 = boto3.client('s3')

        try:
            s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_path)
        except:
            return None
        
def list_s3_bucket(s3_dir):
    logger.info(f'list s3 bucket {s3_dir}')
    if s3_dir.startswith('/'):
        s3_dir = s3_dir[1:]

    if is_s3_emulation:
        s3_dir_full_path = 'http://s3:5000/list_bucket/' + s3_dir
        # s3_dir_full_path = 'http://localhost:5000/list_bucket/' + s3_dir
    else:
        s3_dir_full_path = 's3://' + s3_dir

    all_files = []
    if is_s3_emulation:
        r = requests.get(s3_dir_full_path)
        ret = r.json()
        for entry in ret['Contents']:
            all_files.append(os.path.join(s3_dir.split('/')[0], entry['Key']))
    else:
        # check s3_dir string to see if it contains "pv-validation-hub-bucket/"
        # if so, remove it
        s3_dir = s3_dir.replace('pv-validation-hub-bucket/', '')
        logger.info(f'dir after removing pv-validation-hub-bucket/ returns {s3_dir}')

        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=s3_dir)
        for page in pages:
            if page['KeyCount'] > 0:
                for entry in page['Contents']:
                    all_files.append(entry['Key'])

        # remove the first entry if it is the same as s3_dir
        if len(all_files) > 0 and all_files[0] == s3_dir:
            all_files.pop(0)
    
    logger.info(f'listed s3 bucket {s3_dir_full_path} returns {all_files}')
    return all_files


def update_submission_status(analysis_id, submission_id, new_status):
    r = requests.put(f'http://api:8005/submissions/analysis/{analysis_id}/change_submission_status/{submission_id}',
                     data={'status': new_status})
    if r.status_code != 200:
        print(f"error update submission status to {new_status}, status code {r.status_code} {r.content}", file=sys.stderr)


def update_submission_result(analysis_id, submission_id, result_json):
    headers = {"Content-Type": "application/json"}
    r = requests.put(f'http://api:8005/submissions/analysis/{analysis_id}/update_submission_result/{submission_id}',
                     json=result_json, headers=headers)
    if r.status_code != 200:
        print(f"error update submission result to {result_json}, status code {r.status_code} {r.content}", file=sys.stderr)


def convert_compressed_file_path_to_directory(compressed_file_path):
    path_components = compressed_file_path.split('/')
    path_components[-1] = path_components[-1].split('.')[0]
    path_components = '/'.join(path_components)
    return path_components


def get_file_extension(path):
    return path.split('/')[-1].split('.')[-1]


def decompress_file(path):
    if (get_file_extension(path) == 'gz'):
        with tarfile.open(path, "r:gz") as tar:
            tar.extractall(convert_compressed_file_path_to_directory(path))
    else:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(convert_compressed_file_path_to_directory(path))
    return convert_compressed_file_path_to_directory(path)


def get_module_file_name(module_dir):
    for root, _, files in os.walk(module_dir, topdown=True):
        for name in files:
            if name.endswith('.py'):
                return name.split('/')[-1]


def get_module_name(module_dir):
    return get_module_file_name(module_dir)[:-3]





SUBMITTING = "submitting"
SUBMITTED = "submitted"
RUNNING = "running"
FAILED = "failed"
FINISHED = "finished"

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
            shutil.move(os.path.join(source_dir, file_name),
                        os.path.join(target_dir, file_name))


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


def download_and_extract_zip_file(file_name, download_location, extract_location, new_name=None):
    """
    * Function to extract download a zip file, extract it and then removes the zip file.
    * `download_location` should include name of file as well.
    """
    try:
        s3 = boto3.client(
            's3',
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
    files = list_s3_bucket(f'pv-validation-hub-bucket/evaluation_scripts/{analysis_id}/')
    logger.info(f'pull evaluation scripts from s3')
    for file in files:
        logger.info(f'pull file {file} from s3')
        tmp_path = pull_from_s3(file)
        shutil.move(tmp_path, os.path.join(current_evaluation_dir, tmp_path.split('/')[-1]))
    # create data directory and sub directories
    data_dir = os.path.join(current_evaluation_dir, 'data')
    file_data_dir = os.path.join(data_dir, 'file_data')
    validation_data_dir = os.path.join(data_dir, 'validation_data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(file_data_dir, exist_ok=True)
    os.makedirs(validation_data_dir, exist_ok=True)
    # # move file_test_link
    # shutil.move(os.path.join(current_evaluation_dir, 'file_test_link.csv'),
    #             os.path.join(data_dir, 'file_test_link.csv'))
    # shutil.move(os.path.join(current_evaluation_dir, 'config.json'),
    #             os.path.join(data_dir, 'config.json')) 
    # download data files
    analyticals = list_s3_bucket(f'pv-validation-hub-bucket/data_files/analytical/')
    for analytical in analyticals:
        tmp_path = pull_from_s3(analytical)
        shutil.move(tmp_path, os.path.join(file_data_dir, tmp_path.split('/')[-1]))
    ground_truths = list_s3_bucket(f'pv-validation-hub-bucket/data_files/ground_truth/')
    for ground_truth in ground_truths:
        tmp_path = pull_from_s3(ground_truth)
        shutil.move(tmp_path, os.path.join(validation_data_dir, tmp_path.split('/')[-1]))


def create_current_evaluation_dir(dir_name='current_evaluation'):
    local_dir = dir_name
    logger.info(f'create local folder {local_dir}')
    current_evaluation_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), local_dir)
    logger.info(f'local folder located at {current_evaluation_dir}')
    if not os.path.exists(current_evaluation_dir):
        os.makedirs(current_evaluation_dir)
        logger.info(f'created local folder {current_evaluation_dir}')
    return current_evaluation_dir


def load_analysis(analysis_id, current_evaluation_dir):

    logger.info("pull and extract analysis")
    extract_analysis_data(analysis_id, current_evaluation_dir)
    logger.info("install analysis dependency")
    try:
        subprocess.check_call(["python", "-m", "pip", "install", "-r", os.path.join(current_evaluation_dir, 'requirements.txt')])
        logger.info("analysis dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error("error installing analysis dependencies:", e)
    # Copy the validation runner and insert-analysis class into the current
    # evaluation directory
    shutil.copy(os.path.join('/root/worker', 'pvinsight-validation-runner.py'),
                os.path.join(current_evaluation_dir, 'pvinsight-validation-runner.py'))
    shutil.copy(os.path.join('/root/worker', 'insert-analysis.py'),
                os.path.join(current_evaluation_dir, 'insert-analysis.py'))
    # import analysis runner as a module
    sys.path.insert(0, current_evaluation_dir)
    runner_module_name = 'pvinsight-validation-runner'
    logger.info(f'import runner module {runner_module_name}')
    analysis_module = import_module(runner_module_name)
    sys.path.pop(0)

    analysis_function = getattr(analysis_module, 'run')
    function_parameters = list(inspect.signature(analysis_function).parameters)
    logger.info(f'analysis function parameters: {function_parameters}')
    return analysis_function, function_parameters
    


    


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
    download_and_extract_zip_file("submission_files/submission_{}.zip".format(submission_id), submission_zip_file,
                                  submission_data_directory, "")

    # import as module
    importlib.invalidate_caches()
    submission_module = importlib.import_module(
        SUBMISSION_IMPORT_STRING.format(submission_id=submission_id)
    )
    SUBMISSION_ALGORITHMS[submission_id] = submission_module

    return submission


def run_submission(analysis_id, submission):
    """
    * receives a analysis id and submission object
    * calls evaluation script
    """
    # get test data path
    submission_id = submission.submission_id
    analysis_data_file_path = ANALYSIS_DATA_FILE_PATH.format(
        analysis_id=analysis_id, data_file='test_data')

    # update status as running
    submission.status = Submission.RUNNING
    submission.save()

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
            analysis_data_file_path,
            annotation_file_path,
            SUBMISSION_ALGORITHMS[submission_id].predict
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
        submission_output = json.dumps(submission_output)
        # Submission.objects.filter(submission_id=submission_id).update(
        #     result=submission_output)
        submission.result = submission_output
        submission.status = Submission.FINISHED
        submission.save()
    except Exception as e:
        print(e)
        submission.status = Submission.FAILED


def process_submission_message(message):
    """
    Extracts the submission related metadata from the message
    and send the submission object for evaluation
    """
    analysis_id = int(message.get("analysis_pk"))
    submission_id = int(message.get("submission_pk"))
    user_id = int(message.get("user_pk"))
    submission_filename = message.get("submission_filename")

    current_evaluation_dir = create_current_evaluation_dir()

    analysis_function, function_parameters = load_analysis(analysis_id, current_evaluation_dir)
    logger.info(f'function parameters returns {function_parameters}')

    # execute the runner script
    # assume ret indicates the directory of result of the runner script
    argument = f'pv-validation-hub-bucket/submission_files/submission_user_{user_id}/submission_{submission_id}/{submission_filename}'
    logger.info(f'execute runner module function with argument {argument}')

    ret = analysis_function(argument, current_evaluation_dir)
    logger.info(f'runner module function returns {ret}')

    logger.info(f'update submission status to {FINISHED}')
    update_submission_status(analysis_id, submission_id, FINISHED)

    # Uploads public metrics to DB, ret expected format {'module': 'pvanalytics-cpd-module', 'mean_mean_absolute_error': 2.89657870134743, 'mean_run_time': 24.848265788458676, 'data_requirements': ['time_series', 'latitude', 'longitude', 'data_sampling_frequency']}
    res_json = ret
    logger.info(f'update submission result to {res_json}')
    update_submission_result(analysis_id, submission_id, res_json)

    logger.info(f'upload result files to s3')
   
    res_files_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'current_evaluation/results')
    for dir_path, dir_names, file_names in os.walk(res_files_path):
        for file_name in file_names:
            full_file_name = os.path.join(dir_path, file_name)
            relative_file_name = full_file_name[len(f'{res_files_path}/'):]
            s3_full_path = f'pv-validation-hub-bucket/submission_files/submission_user_{user_id}/submission_{submission_id}/results/{relative_file_name}'
            logger.info(f'upload result file "{full_file_name}" to s3 path "{s3_full_path}"')
            push_to_s3(full_file_name, s3_full_path)

    # remove the current evaluation dir
    logger.info(f'remove directory {current_evaluation_dir}')
    shutil.rmtree(current_evaluation_dir)


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
    # Use the Docker endpoint URL for local development
    if is_s3_emulation:
        sqs = boto3.resource(
            "sqs",
            endpoint_url='http://sqs:9324',
            region_name='elasticmq',
            aws_secret_access_key='x',
            aws_access_key_id='x',
            use_ssl=False
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
            ex.response["Error"]["Code"]
            != "AWS.SimpleQueueService.NonExistentQueue"
        ):
            logger.exception("Cannot get queue: {}".format(queue_name))
        queue = sqs.create_queue(QueueName=queue_name,
                                 Attributes={'FifoQueue': 'true'})
    return queue



def get_analysis_pk():
    instance_id = urllib.request.urlopen(
        'http://169.254.169.254/latest/meta-data/instance-id').read().decode()

    ec2_resource = boto3.resource(
        'ec2',
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
    )
    ec2_instance = ec2_resource.Instance(instance_id)
    tags = ec2_instance.tags
    for tag in tags:
        if tag['Key'] == 'ANALYSIS_PK':
            return int(tag['Value'])
    return 1


def main():
    killer = GracefulKiller()
    logger.info(
        "{} Using {} as temp directory to store data".format(
            WORKER_LOGS_PREFIX, BASE_TEMP_DIR
        )
    )
    queue = get_or_create_sqs_queue("valhub_submission_queue.fifo")
    # print(queue)

    # infinite loop to listen and process messages
    while True:
        messages = queue.receive_messages(
            MaxNumberOfMessages=1,
            VisibilityTimeout=7200
        )
        for message in messages:
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
