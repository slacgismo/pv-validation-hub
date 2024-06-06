from typing import Any
import os
import json
from utility import (
    generate_private_report_for_submission,
)
import logging

logger = logging.getLogger(__name__)


def main(action: str = "export"):
    action = action.lower()

    data_file_path = os.path.join(os.path.dirname(__file__), "data.json")

    html_file_path = os.path.join(os.path.dirname(__file__), "template.html")

    json_data: dict[str, Any] = {}

    with open(data_file_path, "r") as data_file:
        json_data = json.load(data_file)

    generate_private_report_for_submission(json_data, action, html_file_path)


if __name__ == "__main__":

    main(action="export")
