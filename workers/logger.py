import logging
import logging.config
import os
import json
from typing import Any


def setup_logging():
    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logging_config.json"
    )

    with open(config_file_path, "r") as f:
        config: dict[str, Any] = json.load(f)

    logging.config.dictConfig(config)
