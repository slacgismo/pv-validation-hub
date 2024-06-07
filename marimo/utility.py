from typing import Any, TypeVar
import subprocess
import json
import pandas as pd
from logging import Logger

import logging

T = TypeVar("T")


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


def flatten_list(items: list[T]) -> list[T]:
    flat_list: list[T] = []
    for item in items:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def format_tuple(
    t: tuple[str, Any], logger: Logger | None = None
) -> str | list[str]:
    key, value = t

    logger_if_able(
        f"key: {key}, value: {value}, type: {type(value)}", logger, "DEBUG"
    )

    if isinstance(value, (int, float)):
        return f"--{key}={value}"

    if isinstance(value, str):
        if " " in [value]:
            return f'--{key}="{value}"'
        return f"--{key}={value}"

    if isinstance(value, (dict)):
        try:
            json_str = json.dumps(value)
        except Exception as e:
            raise ValueError(f"Failed to convert to JSON: {e}")

        return f"--{key}={json_str}"

    if isinstance(value, bool):
        return f"--{key}={str(value).lower()}"

    if isinstance(value, list):
        list_args: list[str] = []
        for item in value:
            formatted_item = format_tuple((key, item))
            if isinstance(formatted_item, list):
                list_args.extend(flatten_list(formatted_item))
            if isinstance(formatted_item, str):
                list_args.append(formatted_item)
        return list_args

    raise ValueError(f"Unsupported type: {type(value)}")


def prepare_json_for_marimo_args(json_data: dict[str, Any]):

    args_list: list[str] = []

    for key, value in json_data.items():

        args = format_tuple((key, value))

        if isinstance(args, list):
            args_list.extend(flatten_list(args))
        if isinstance(args, str):
            args_list.append(args)

    return args_list


def generate_private_report_for_submission(
    df: pd.DataFrame,
    action: str,
    template_file_path: str,
    html_file_path: str,
    logger: Logger | None = None,
):
    json_data: dict[str, Any] = {}
    json_data["results_df"] = df.to_dict(orient="records")

    data_args_list = prepare_json_for_marimo_args(json_data)

    if not data_args_list or len(data_args_list) == 0:
        raise ValueError("No data to pass to marimo")

    logger_if_able(f"Data as args: {data_args_list}", logger, "DEBUG")

    cli_commands = {
        "export": [
            "marimo",
            "export",
            "html",
            f"{template_file_path}",
            "-o",
            f"{html_file_path}",
            "--no-include-code",
            "--",
            *data_args_list,
        ],
        "edit": [
            "marimo",
            "edit",
            f"{template_file_path}",
            "--",
            *data_args_list,
        ],
        "run": [
            "marimo",
            "run",
            f"{template_file_path}",
            "--",
            *data_args_list,
        ],
    }

    if action not in cli_commands.keys():
        raise ValueError("Unsupported command")

    try:
        subprocess.run(
            cli_commands[action],
            check=True,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
        )
    except Exception as e:
        logger_if_able(f"Error: {e}", logger, "ERROR")
        return
