import re
import os
import sys


VALID_FORMAT_REGEX = (
    r"^(([a-zA-Z][a-zA-Z0-9\-_\[\],]*)(([<>=!~]=?)[0-9.*]+,?)*)$"
)
PACKAGE_NAME_REGEX = r"^([a-zA-Z][a-zA-Z0-9\-\_\,]*)"


def is_valid_package(package: str):
    """
    Check if the package name is in the correct format.
    """
    if not re.match(VALID_FORMAT_REGEX, package):
        print(f"Invalid package name: {package}")
        return False
    return True


def get_package_name(package: str):
    """
    Get the package name from the package string.
    """

    match = re.match(PACKAGE_NAME_REGEX, package)
    if match:
        return match.group(1)
    return None


def check_requirements(requirements: list[str], whitelist: list[str]):
    """
    Check if the requirements are in the correct format.
    """
    for package in requirements:
        name = package.strip().replace(" ", "").lower()
        if not is_valid_package(name):
            print(f"Invalid package name: {name}")
            sys.exit(5)
        package_name = get_package_name(name)
        if not package_name:
            print(f"Invalid package name: {name}")
            sys.exit(5)
        if package_name not in whitelist:
            print(
                f"Package {package_name} is not in the whitelist of approved packages."
            )
            sys.exit(6)
    return True


def main(arguments: list[str]):
    """
    Main function to check requirements.
    """
    if len(arguments) == 0:
        print("No arguments provided.")
        sys.exit(1)

    if len(arguments) != 2:
        print("Invalid number of arguments.")
        sys.exit(1)

    # Check if requirements.txt exists
    requirements_path = arguments[0]
    whitelist_path = arguments[1]
    if not os.path.exists(requirements_path):
        print(f"{requirements_path} does not exist.")
        sys.exit(2)
    if not os.path.exists(whitelist_path):
        print(f"{whitelist_path} does not exist.")
        sys.exit(3)

    with open(requirements_path, "r") as f:
        lines = f.readlines()
        requirements = [x.strip() for x in lines]

    with open(whitelist_path, "r") as f:
        lines = f.readlines()
        whitelist = [x.strip() for x in lines]

    is_valid = check_requirements(requirements, whitelist)
    if not is_valid:
        print("Invalid requirements.")
        sys.exit(4)
    print("All requirements are valid.")
    sys.exit(0)


if __name__ == "__main__":
    arguments = sys.argv[1:]

    main(arguments)
