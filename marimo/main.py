import os
import pandas as pd
from utility import (
    generate_private_report_for_submission,
)
import logging

logger = logging.getLogger(__name__)


def main(action: str = "export"):
    action = action.lower()

    data_file_path = os.path.join(
        os.path.dirname(__file__), "time_shifts_full_results.csv"
    )

    html_file_path = os.path.join(os.path.dirname(__file__), "template.html")
    template_file_path = os.path.join(os.path.dirname(__file__), "template.py")

    df = pd.DataFrame()

    with open(data_file_path, "r") as data_file:
        df = pd.read_csv(data_file)

    generate_private_report_for_submission(
        df, action, template_file_path, html_file_path
    )


if __name__ == "__main__":

    main(action="export")
