from typing import Any, TypeVar
import marimo
import subprocess
import os
import json

T = TypeVar("T")


def flatten_list(items: list[T]) -> list[T]:
    flat_list: list[T] = []
    for item in items:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def format_tuple(t: tuple[str, Any]) -> str | list[str]:
    key, value = t

    print(f"key: {key}, value: {value}, type: {type(value)}")

    if isinstance(value, (int, float)):
        return f"--{key}={value}"

    if isinstance(value, str):
        if " " in [value]:
            return f'--{key}="{value}"'
        return f"--{key}={value}"

    if isinstance(value, (dict)):

        json_str = json.dumps(value)

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


def main(command: str = "export"):
    command = command.lower()

    if command not in ["export", "edit", "run"]:
        raise ValueError("Unsupported command")

    data_file_path = os.path.join(os.path.dirname(__file__), "data.json")

    html_file_path = os.path.join(os.path.dirname(__file__), "template.html")

    json_data: dict[str, Any] = {}

    with open(data_file_path, "r") as data_file:
        json_data = json.load(data_file)

    data_as_args = prepare_json_for_marimo_args(json_data)

    if not data_as_args or len(data_as_args) == 0:
        raise ValueError("No data to pass to marimo")

    print(f"Data as args: {data_as_args}")

    json.loads(json.dumps(json_data))

    cli_command = {
        "export": [
            "marimo",
            "export",
            "html",
            "template.py",
            "-o",
            f"{html_file_path}",
            "--no-include-code",
            "--",
            *data_as_args,
        ],
        "edit": [
            "marimo",
            "edit",
            "template.py",
            "--",
            *data_as_args,
        ],
        "run": [
            "marimo",
            "run",
            "template.py",
            "--",
            *data_as_args,
        ],
    }

    subprocess.run(
        [
            *cli_command[command],
        ],
        check=True,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
    )


if __name__ == "__main__":

    main(command="export")
