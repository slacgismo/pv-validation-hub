from importlib import import_module
import inspect
import sys
import os
import zipfile
import tarfile
import shutil
from typing import Callable, cast

import logging

logger = logging.getLogger(__name__)


def extract_files(  # noqa: C901
    ref: zipfile.ZipFile | tarfile.TarFile,
    extract_path: str,
    zip_path: str,
    remove_unallowed_starting_characters: Callable[[str], str | None],
):

    logger.info("Extracting files from: " + zip_path)

    if ref.__class__ == zipfile.ZipFile:
        ref = cast(zipfile.ZipFile, ref)
        file_names = ref.namelist()
    elif ref.__class__ == tarfile.TarFile:
        ref = cast(tarfile.TarFile, ref)
        file_names = ref.getnames()
    else:
        raise Exception("File is not a zip or tar file.")

    # recursively remove files and folders that start with certain characters
    file_names = [
        f for f in file_names if remove_unallowed_starting_characters(f)
    ]
    logger.info("File names:")
    logger.info(file_names)
    folders = [f for f in file_names if f.endswith("/")]
    logger.info("Folders:")
    logger.info(folders)

    if len(folders) == 0:
        logger.info("Extracting all files...")

        for file in file_names:
            if ref.__class__ == zipfile.ZipFile:
                ref = cast(zipfile.ZipFile, ref)
                ref.extract(file, path=extract_path)
            elif ref.__class__ == tarfile.TarFile:
                ref = cast(tarfile.TarFile, ref)
                ref.extract(file, path=extract_path, filter="data")
            else:
                raise Exception("File is not a zip or tar file.")

    else:
        # if all files have the same root any folder can be used to check since all will have the same root if true
        do_all_files_have_same_root = all(
            [f.startswith(folders[0]) for f in file_names]
        )
        logger.info(
            "Do all files have the same root? "
            + str(do_all_files_have_same_root)
        )

        if do_all_files_have_same_root:
            # extract all files within the folder with folder of the zipfile that has the same root
            root_folder_name = folders[0]

            logger.info("Extracting files...")
            for file in file_names:
                if file.endswith("/") and file != root_folder_name:
                    os.makedirs(
                        os.path.join(
                            extract_path,
                            file.removeprefix(root_folder_name),
                        )
                    )
                if not file.endswith("/"):
                    if ref.__class__ == zipfile.ZipFile:
                        ref = cast(zipfile.ZipFile, ref)
                        ref.extract(file, path=extract_path)
                    elif ref.__class__ == tarfile.TarFile:
                        ref = cast(tarfile.TarFile, ref)
                        ref.extract(file, path=extract_path, filter="data")
                    else:
                        raise Exception(1, "File is not a zip or tar file.")

                    os.rename(
                        os.path.join(extract_path, file),
                        os.path.join(
                            extract_path,
                            file.removeprefix(root_folder_name),
                        ),
                    )

            # remove the root folder and all other folders
            shutil.rmtree(os.path.join(extract_path, root_folder_name))

        else:
            logger.info("Extracting all files...")
            for file in file_names:
                if ref.__class__ == zipfile.ZipFile:
                    ref = cast(zipfile.ZipFile, ref)
                    ref.extract(file, path=extract_path)
                elif ref.__class__ == tarfile.TarFile:
                    ref = cast(tarfile.TarFile, ref)
                    ref.extract(file, path=extract_path, filter="data")
                else:
                    raise Exception(1, "File is not a zip or tar file.")


def extract_zip(zip_path: str, extract_path: str):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    def remove_unallowed_starting_characters(file_name: str) -> str | None:
        unallowed_starting_characters = ("_", ".")

        parts = file_name.split("/")
        for part in parts:
            if part.startswith(unallowed_starting_characters):
                return None
        return file_name

    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            extract_files(
                zip_ref,
                extract_path,
                zip_path,
                remove_unallowed_starting_characters,
            )
    elif tarfile.is_tarfile(zip_path):
        with tarfile.open(zip_path, "r") as tar_ref:
            extract_files(
                tar_ref,
                extract_path,
                zip_path,
                remove_unallowed_starting_characters,
            )
    else:
        raise Exception(1, "File is not a zip or tar file.")


def format_args_for_submission(args):
    return args


def import_submission_function(submission_file_name: str, function_name: str):
    # Dynamically import function from submission.py
    try:
        submission_module = import_module(submission_file_name)
    except ModuleNotFoundError as e:
        logger.info(f"ModuleNotFoundError: {submission_file_name} not found")
        raise e

    try:
        submission_function: Callable = getattr(
            submission_module, function_name
        )
        function_parameters = list(
            inspect.signature(submission_function).parameters.keys()
        )
    except AttributeError as e:
        logger.info(
            f"AttributeError: {function_name} not found in submission module"
        )
        raise e

    return submission_function, function_parameters


def main():
    args = sys.argv[1:]

    if len(args) < 1:
        logger.info("Function name not provided")
        sys.exit(1)

    submission_file_name = args[0]
    function_name = args[1]

    submission_zip_file_path = os.path.join(
        os.path.dirname(__file__), f"{submission_file_name}.zip"
    )

    logger.info(f"Submission zip file path: {submission_zip_file_path}")
    extract_zip(submission_zip_file_path, ".")

    if not os.path.exists(submission_file_name):
        logger.error(f"Submission file not found: {submission_file_name}")
        sys.exit(1)

    submission_function, function_parameters = import_submission_function(
        submission_file_name, function_name
    )

    logger.info(f"Submission file name: {submission_file_name}")
    logger.info(f"Function name: {function_name}")
    logger.info(f"Function: {submission_function}")
    logger.info(f"Function parameters: {function_parameters}")

    submission_args = format_args_for_submission(args[2:])

    results = submission_function(*submission_args)
    logger.info(f"Results: {results}")


if __name__ == "__main__":
    main()
