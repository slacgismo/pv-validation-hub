from functools import wraps
import os
import hashlib
import pandas as pd
import numpy as np
import boto3
from botocore.exceptions import (
    NoCredentialsError,
    PartialCredentialsError,
    ClientError,
)
from mypy_boto3_s3 import S3Client
import requests
import logging
from logging import Logger
from typing import Any, Callable, TypeVar, ParamSpec
import json

T = TypeVar("T")
P = ParamSpec("P")

logger = logging.getLogger(__name__)


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return "PROD" not in os.environ


IS_LOCAL = is_local()


def logger_if_able(
    message: str, logger: Logger | None = None, level: str = "INFO"
):
    if logger is not None:
        levels_dict = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        level = level.upper()

        if level not in levels_dict:
            raise Exception(f"Invalid log level: {level}")

        log_level = levels_dict[level]

        logger.log(log_level, message)
    else:
        print(message)


def request_handler(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    r = method_request(method, endpoint, headers=headers, data=data)
    if not r.ok:
        logger_if_able(f"Error: {r.text}", logger, "ERROR")
        raise Exception("Failed to get data")
    logger_if_able(r.text, logger)
    json_body: dict[str, Any] = json.loads(r.text)
    return json_body


def method_request(
    method: str,
    url: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    logger_if_able(f"{method} request to {url}", logger)

    base_headers = {
        "Content-Type": "application/json",
    }

    all_headers: dict[str, str] = (
        {**base_headers, **headers} if headers else base_headers
    )

    body = json.dumps(data) if data else None

    response = requests.request(method, url, headers=all_headers, data=body)

    return response


def login_to_API(
    api_url: str, username: str, password: str, logger: Logger | None = None
):

    login_url = f"{api_url}/login"

    json_body = request_handler(
        "POST", login_url, {"username": username, "password": password}
    )

    if "token" not in json_body:
        logger_if_able("Token not in response", logger, "ERROR")
        raise Exception("Token not in response")
    token: str = json_body["token"]
    return token


def with_credentials(api_url: str, logger: Logger | None = None):

    username = os.environ.get("admin_username")
    password = os.environ.get("admin_password")

    if not username or not password:
        raise Exception("Missing admin credentials")

    api_auth_token = None
    headers = {}

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            nonlocal api_auth_token
            if not api_auth_token:
                logger_if_able("Logging in", logger)
                api_auth_token = login_to_API(
                    api_url, username, password, logger
                )
                headers["Authorization"] = f"Token {api_auth_token}"
            kwargs["auth"] = headers
            return func(*args, **kwargs)

        return wrapper

    return decorator


def request_to_API(
    api_url: str,
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    url = f"{api_url}/{endpoint}"

    data = request_handler(method, url, data, headers, logger)
    return data


def get_file_hash(file_path: str):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def get_s3_file_hash(
    s3_client: S3Client, bucket_name: str, file_key: str
) -> str:
    s3_file_hash = s3_client.get_object(Bucket=bucket_name, Key=file_key)[
        "ETag"
    ].replace('"', "")
    return s3_file_hash


def get_s3_file_hash_for_list_of_files(
    file_paths: list[str], s3_client: S3Client, bucket_name: str
) -> str:
    hashes: list[str] = []
    for file_key in file_paths:
        s3_file_hash = get_s3_file_hash(s3_client, bucket_name, file_key)
        hashes.append(s3_file_hash)

    combined_hash = combine_hashes(hashes)

    return combined_hash


def get_hash_for_list_of_files(file_paths: list[str]) -> str:
    individual_hashes = [get_file_hash(file_path) for file_path in file_paths]
    combined_hash = combine_hashes(individual_hashes)
    return combined_hash


def are_hashes_the_same(local_hash: str, s3_hash: str) -> bool:
    return local_hash == s3_hash


def combine_hashes(hashes: list[str]) -> str:
    combined_hasher = hashlib.md5()
    for hash in hashes:
        combined_hasher.update(hash.encode())
    return combined_hasher.hexdigest()


def request_to_API_w_credentials(
    api_url: str,
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
    **kwargs: Any,
):

    url = f"{api_url}/{endpoint}"
    print(url)
    auth_header: dict[str, str] | None = (
        kwargs["auth"] if "auth" in kwargs else None
    )

    if auth_header is None:
        raise Exception("No auth header found")

    if headers is None:
        headers = {}

    headers = {**headers, **auth_header}

    response = request_handler(method, url, data, headers, logger)
    return response


# Fetch data from the remote API
def get_data_from_api_to_df(
    api_url: str, endpoint: str, logger: Logger | None = None
) -> pd.DataFrame:

    response = with_credentials(api_url, logger)(request_to_API_w_credentials)(
        api_url, "GET", endpoint=endpoint, logger=logger
    )

    # # Check if the data is a dictionary of scalar values
    # if all(np.isscalar(v) for v in data.values()):
    #     # If it is, wrap the values in lists
    #     data = {k: [v] for k, v in data.items()}
    return pd.DataFrame(response)


def post_data_to_api_to_df(
    api_url: str,
    endpoint: str,
    data: dict[str, Any],
    logger: Logger | None = None,
) -> pd.DataFrame:

    response: dict[str, Any] | list[Any] = with_credentials(api_url, logger)(
        request_to_API_w_credentials
    )(api_url, "POST", endpoint=endpoint, data=data)

    # Check if the data is a dictionary of scalar values
    if all(np.isscalar(v) for v in response.values()):
        # If it is, wrap the values in lists
        response = {k: [v] for k, v in response.items()}
    return pd.DataFrame(response)


def hasAllColumns(df: pd.DataFrame, cols: list[str]):
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
    aws_profile_name: str = "default",  # Default AWS profile name,
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

            logger.info(s3_file_full_path, file_content[:100])
            # exit()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                logger.info(
                    f"error put file {upload_path} to s3, status code {r.status_code} {r.content}"
                )
                return None
            else:
                return s3_file_full_path.replace(
                    f"{s3_url}/put_object/", f"{s3_url}/get_object/"
                )
    else:
        """Upload file to S3 bucket and return object URL"""
        session = boto3.Session(profile_name=aws_profile_name)
        s3: S3Client = session.client("s3")  # type: ignore

        try:
            logger.info(
                f"uploading {local_path} to {bucket_name}/{upload_path}"
            )
            s3.upload_file(local_path, bucket_name, upload_path)
            logger.info(
                f"uploaded {local_path} to {bucket_name}/{upload_path}"
            )
        except Exception as e:
            logger.info(
                f"error uploading {local_path} to {bucket_name}/{upload_path}"
            )
            raise e

        bucket_location = s3.get_bucket_location(Bucket=bucket_name)
        object_url = "https://{}.s3.{}.amazonaws.com/{}".format(
            bucket_name, bucket_location["LocationConstraint"], upload_path
        )
        logger.info(
            f"uploaded {local_path} to {bucket_name}/{upload_path} returns {object_url}"
        )
        return object_url


def list_s3_bucket(
    is_s3_emulation: bool,
    s3_bucket_name: str,
    s3_dir: str,
    aws_profile_name: str = "default",
) -> list[str]:
    logger.info(f"list s3 bucket {s3_dir}")
    if s3_dir.startswith("/"):
        s3_dir = s3_dir[1:]

    if is_s3_emulation:
        s3_dir_full_path = "http://s3:5000/list_bucket/" + s3_dir
        # s3_dir_full_path = 'http://127.0.0.1:5000/list_bucket/' + s3_dir
    else:
        s3_dir_full_path = f"s3://{s3_bucket_name}/{s3_dir}"

    all_files: list[str] = []
    if is_s3_emulation:
        r = requests.get(s3_dir_full_path)
        ret = r.json()
        for entry in ret["Contents"]:
            all_files.append(os.path.join(s3_dir.split("/")[0], entry["Key"]))
    else:
        session = boto3.Session(profile_name=aws_profile_name)
        s3: S3Client = session.client("s3")  # type: ignore
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

    logger.info(f"listed s3 bucket {s3_dir_full_path} returns {all_files}")
    return all_files


def pull_from_s3(
    IS_LOCAL: bool,
    S3_BUCKET_NAME: str,
    s3_file_path: str,
    local_file_path: str,
    logger: logging.Logger,
    aws_profile_name: str = "default",  # Default AWS profile name
) -> str:
    logger.info(f"pull file {s3_file_path} from s3")
    if s3_file_path.startswith("/"):
        s3_file_path = s3_file_path[1:]

    if IS_LOCAL:
        logger.info("running locally")
        s3_file_full_path = "http://s3:5000/get_object/" + s3_file_path
        # s3_file_full_path = 'http://127.0.0.1:5000/get_object/' + s3_file_path
    else:
        logger.info("running in ecs")
        s3_file_full_path = f"s3://{S3_BUCKET_NAME}/{s3_file_path}"

    target_file_path = os.path.join(
        local_file_path, s3_file_full_path.split("/")[-1]
    )

    if IS_LOCAL:
        r = requests.get(s3_file_full_path, stream=True)
        if not r.ok:
            logger.error(f"Error: {r.content}")

            raise requests.HTTPError(
                2, f"Error downloading file from s3: {r.content}"
            )
        with open(target_file_path, "wb") as f:
            f.write(r.content)
    else:
        session = boto3.Session(profile_name=aws_profile_name)
        s3: S3Client = session.client("s3")  # type: ignore
        try:
            logger.info(
                f"Downloading {s3_file_path} from {S3_BUCKET_NAME} to {target_file_path}"
            )
            s3.download_file(S3_BUCKET_NAME, s3_file_path, target_file_path)

        except ClientError as e:
            logger.error(f"Error: {e}")
            raise requests.HTTPError(
                2, f"File {target_file_path} not found in s3 bucket."
            )

    return target_file_path


def check_aws_credentials(profile_name: str = "default"):
    try:
        # Create a session using the default profile
        session = boto3.Session(profile_name=profile_name)
        # Get the credentials
        credentials = session.get_credentials()
        # Check if credentials are available
        if credentials is None:
            raise NoCredentialsError
        # Check if the credentials are complete
        credentials.get_frozen_credentials()
        print("AWS credentials are available.")
    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials are not available or incomplete.")
