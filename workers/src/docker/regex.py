import re


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
            continue
        package_name = get_package_name(name)
        if not package_name:
            print(f"Invalid package name: {name}")
            continue
        if package_name not in whitelist:
            print(f"Package {package_name} is whitelisted.")
            raise ValueError(
                f"Package {package_name} is not in the whitelist."
            )
    print("All packages are valid and whitelisted.")


def main():
    """
    Main function to check requirements.
    """
    requirements = open("requirements.txt").readlines()
    requirements = [x.strip() for x in requirements]
    whitelist = open("whitelist-packages.txt").readlines()
    whitelist = [x.strip() for x in whitelist]

    check_requirements(requirements, whitelist)


if __name__ == "__main__":
    main()
