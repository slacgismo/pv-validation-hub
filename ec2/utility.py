import os
import requests
import logging
from logging import Logger
from typing import Any, Callable, TypeVar
import json

T = TypeVar("T")


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return "PROD" not in os.environ


IS_LOCAL = is_local()

API_BASE_URL = (
    "http://api:8005" if IS_LOCAL else "http://api.pv-validation-hub.org"
)

S3_BASE_URL = "http://s3:5000/get_object/" if IS_LOCAL else "s3://"


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

    all_headers = {**base_headers, **headers} if headers else base_headers

    body = json.dumps(data) if data else None

    response = requests.request(method, url, headers=all_headers, data=body)

    return response


def login_to_API(username: str, password: str, logger: Logger | None = None):

    login_url = f"{API_BASE_URL}/login"

    json_body = request_handler(
        "POST", login_url, {"username": username, "password": password}
    )

    if "token" not in json_body:
        logger_if_able("Token not in response", logger, "ERROR")
        raise Exception("Token not in response")
    token: str = json_body["token"]
    return token


def with_credentials(logger: Logger | None = None):

    username = os.environ.get("admin_username")
    password = os.environ.get("admin_password")

    if not username or not password:
        raise Exception("Missing admin credentials")

    api_auth_token = None
    headers = {}

    def decorator(func: Callable[..., T]):
        # @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal api_auth_token
            if not api_auth_token:
                logger_if_able("Logging in", logger)
                api_auth_token = login_to_API(username, password, logger)
                headers["Authorization"] = f"Token {api_auth_token}"
            kwargs["auth"] = headers
            return func(*args, **kwargs)

        return wrapper

    return decorator


@with_credentials()
def request_to_API_w_credentials(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
    **kwargs: Any,
):

    url = f"{API_BASE_URL}/{endpoint}"

    auth_header: dict[str, str] | None = (
        kwargs["auth"] if "auth" in kwargs else None
    )

    if auth_header is None:
        raise Exception("No auth header found")

    if headers is None:
        headers = {}

    headers = {**headers, **auth_header}

    data = request_handler(method, url, data, headers, logger)
    return data


def request_to_API(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    logger: Logger | None = None,
):

    url = f"{API_BASE_URL}/{endpoint}"

    data = request_handler(method, url, data, headers, logger)
    return data
