import argparse
import os
import pprint
import json
import boto3
from botocore.exceptions import ClientError
import time
import sys


# --------------------------------------------------------------------------------
def evaluate_for_new_creds(role_name, account_id, display=True):
    """
    NOTE!!: This is specifically targeting a converted version of the
    CSC aws-ss-tool v1.1 executable into aws_sso_tool.py. This structure
    is more preferrable to access for PVDRDB work. eventually this
    will be replaced by pip installed version,  import , and call to a new
    module for the aws-sso-tool in a future version. This should not affect
    any of the functionality, only the method to trigger.

    Makes a call to the CSC Cloud-tools module. Call will evaluate
    if credentials have expired (by time) and make a call to AWS
    systems to generate a new access key, secret access key , and
    session token. Results will be stored into the aws/credential file
    found in the user's home driectory.

    Parameters:
    -------------------------------
    profile : str - target profile name to associate with creds
    account_id : int - aws account id associated with the role/profile name

    Returns
    -------------------------------
    cred_dict : dict - current_creds from AWS Cli. These are synced to expiration
    """
    # Get location of module and append to path to faciltiate import
    file_dir = os.path.dirname(__file__)
    sys.path.append(file_dir)
    import aws_sso_tool

    # Spawn new process and pull creds
    parameters = (
        "--role-name " + role_name + " --account-id " + str(account_id)
    )
    command = (
        'python "'
        + file_dir
        + '/aws_sso_tool.py" get-credentials '
        + parameters
    )
    # print(f'command = {command}')
    os.system(command)

    # Delay to allow for AWS query and write before returning to implement
    # cred scraping from file.
    time.sleep(2)

    # Pull new creds from file.
    # extract and parse config and build into a dict
    home_directory = os.path.expanduser("~")
    # filename is a hash of a dict containing
    # AWS start URL(canned) +  role_name + account_id
    hashed_filename = aws_sso_tool.get_permission_set_credentials_hash_key(
        role_name, str(account_id)
    )
    cli_token_file = (
        home_directory + "/.aws/cli/cache/" + hashed_filename + ".json"
    )
    cred_dict = {}
    if os.path.exists(cli_token_file):
        # print ('AWS Cli cache file identified.')
        # extract contents and format structure
        with open(cli_token_file, "r") as f:
            cred_dict = eval(f.read())
            if display:
                print(cred_dict)
            target_profile = str(account_id) + "_" + role_name
            cred_dict[target_profile] = cred_dict["Credentials"]
            del cred_dict["Credentials"]
            if "ProviderType" in cred_dict.keys():
                del cred_dict["ProviderType"]
            if "Expiration" in cred_dict[target_profile].keys():
                del cred_dict[target_profile]["Expiration"]
            cred_dict[target_profile]["key"] = cred_dict[target_profile][
                "AccessKeyId"
            ]
            del cred_dict[target_profile]["AccessKeyId"]
            cred_dict[target_profile]["secret"] = cred_dict[target_profile][
                "SecretAccessKey"
            ]
            del cred_dict[target_profile]["SecretAccessKey"]
            cred_dict[target_profile]["token"] = cred_dict[target_profile][
                "SessionToken"
            ]
            del cred_dict[target_profile]["SessionToken"]
    else:
        print(" ~/.aws/cli/cache/profile_creds_file.json does not exist")

    return cred_dict


# ----------------------------------------------------------------------------------
def extract_profile_account_id(profile, display=True):
    """
    Will search aws/config file for account id for a particular profile

    Parameters:
    -------------------------------
    profile : str - name of the profile in aws config file.
    display : bool - Default True. Will print to console id.

    Returns
    -------------------------------
    account_id : int - AWS account id associated with the profile
    """
    account_id = 0
    aws_config = {}
    # find users .aws config file in standard location
    home_directory = os.path.expanduser("~")

    # extract and parse config and build into a dict
    aws_config_file = home_directory + "/.aws/config"
    if os.path.exists(aws_config_file):
        print("Found AWS configuration file.")
        with open(aws_config_file, "r") as f:
            text = f.read()
        if text:
            text_lines = text.splitlines()
            for line in text_lines:
                if (line.startswith("[")) and (line.endswith("]")):
                    master_key = line.replace("[", "").replace("]", "")
                    tmp_dict = {}
                else:
                    if line:
                        line_parts = line.split("=")
                        if "sso_region" in line:
                            tmp_dict["sso_region"] = line_parts[1]
                            aws_config[master_key] = tmp_dict
                        elif "region" in line:
                            tmp_dict["region"] = line_parts[1]
                        elif "output" in line:
                            tmp_dict["output"] = line_parts[1]
                        elif "sso_start_url" in line:
                            tmp_dict["sso_start_url"] = line_parts[1]
                        elif "sso_account_id" in line:
                            tmp_dict["sso_account_id"] = line_parts[1]
                        elif "sso_role_name" in line:
                            tmp_dict["sso_role_name"] = line_parts[1]

    # Find profile key in dict and send back profile dict
    for key, val in aws_config.items():
        if profile in key:
            return val

    # No account_id found if here.
    print("No account ID found for profile %s", profile)
    return account_id  # 0


# ----------------------------------------------------------------------------------
def write_credentials(current_role_creds, all_creds, target_cred_name):
    """
    Takes current (unexpired) creds and writes those into the
    ~/.aws/credentials file.

    Parameters:
    -------------------------------
    current_role_creds : dict - contents of the credentials file
    Returns
    -------------------------------
    bool  - status of success of write.
    """
    # find users .aws cred file in standard location
    home_directory = os.path.expanduser("~")
    # extract and parse creds and build into a dict
    aws_creds_file = home_directory + "/.aws/credentials"
    if os.path.exists(aws_creds_file):
        print("Found AWS credentials file.")
        all_creds[target_cred_name] = current_role_creds[target_cred_name]
        # print ('swapped creds')
        file_string = ""
        # print(current_role_creds)
        for key, creds in all_creds.items():
            file_string += "[" + key + "]\n"
            for cred, val in creds.items():
                # print (key, cred, val)
                if cred == "key":
                    file_string += "aws_access_key_id = " + val + "\n"
                elif cred == "secret":
                    file_string += "aws_secret_access_key = " + val + "\n"
                    if "service-creds" in key:
                        file_string += (
                            "\n"  # add extra retrun if service cred.
                        )
                elif cred == "token":
                    file_string += "aws_session_token = " + val + "\n\n"

        try:
            with open(aws_creds_file, "w") as f:
                f.write(file_string)
        except IOError as e:
            print("Error writing to creds file " + str(e))
            return False

    return True


# ----------------------------------------------------------------------------------
def load_config(profile, display=True):
    """
    Will check for new creds if needed and then parse the target
    profile creds or all the creds

    Parameters:
    -------------------------------
    profile : str - name of the profile in aws config file. Leave blank for all.
    display : bool - Default True. Will print to console new creds.

    Returns
    -------------------------------
    aws_creds : dict - a dictionary of the target or all profiles current credentials
    """
    aws_creds = {}
    profile_dict = {}
    if "service-creds" not in profile:
        # Find associated account_id in config file, for profile
        profile_dict = extract_profile_account_id(profile)
        if not profile_dict.get("sso_account_id"):
            print(
                "Account_id for profile %s, not found. Halting program."
                + "Examine or correct .aws/config file in your home directory.",
                profile,
            )
            quit()

        # spawn process to check for new creds and SSO tokens, if needed
        current_role_creds = evaluate_for_new_creds(
            profile, int(profile_dict.get("sso_account_id")), display=display
        )

    # find users .aws cred file in standard location
    home_directory = os.path.expanduser("~")
    # extract and parse creds and build into a dict
    aws_creds_file = home_directory + "/.aws/credentials"
    if not os.path.exists(aws_creds_file):
        # File not there? Make an empty one.
        with open(aws_creds_file, "w") as new_file:
            pass
    # Either existing file or new file should be there
    if os.path.exists(aws_creds_file):
        print("Found AWS credentials file.")
        with open(aws_creds_file, "r") as f:
            text = f.read()
        if text:
            text_lines = text.splitlines()
            for i, line in enumerate(text_lines):
                if (line.startswith("[")) and (line.endswith("]")):
                    master_key = line.replace("[", "").replace("]", "")
                    tmp_dict = {}
                else:
                    if line:
                        line_parts = line.split("=")
                        if "aws_access_key_id" in line:
                            tmp_dict["key"] = line_parts[1].strip()
                        elif "aws_secret_access_key" in line:
                            tmp_dict["secret"] = line_parts[1].strip()
                            # Check to see if this is a service cred account. If so skip the session token.
                            if "service-creds" in text_lines[i - 2]:
                                aws_creds[master_key] = tmp_dict
                        elif "aws_session_token" in line:
                            tmp_dict["token"] = line_parts[1].strip()
                            aws_creds[master_key] = tmp_dict

        # Store all creds off if needed
        all_creds = aws_creds.copy()
        # remove all but target creds for app (all, if target_cred is empty)
        if profile_dict:
            target_cred_name = (
                str(profile_dict.get("sso_account_id")).strip()
                + "_"
                + profile_dict.get("sso_role_name").strip()
            )
        else:
            target_cred_name = profile

        if target_cred_name in aws_creds.keys():
            target_creds = aws_creds[target_cred_name]
            aws_creds.clear()
            aws_creds[target_cred_name] = target_creds

            # Are stored creds same as current_role_creds
            if "service-creds" not in profile:
                if aws_creds != current_role_creds:
                    print(
                        "Creds are out of synch. Write current creds to user's credential file."
                    )
                    if write_credentials(
                        current_role_creds, all_creds, target_cred_name
                    ):
                        aws_creds = current_role_creds
                    # Return empty creds
                    else:
                        return {}
                else:  # new creds not in file.
                    if write_credentials(
                        current_role_creds, all_creds, target_cred_name
                    ):
                        aws_creds = current_role_creds

        # Display creds if flagged
        if display:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(aws_creds)
    else:
        raise FileNotFoundError(
            "AWS file 'credentials' does not exists in the .aws directory, Please locate this file."
        )

    return aws_creds


# --------------------------------------------------------------------------------------------------------------
# Main for testing code and response
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-role-name",
        type=str,
        help="Target profile name as shown in aws/config file",
    )
    parser.add_argument(
        "-account-id",
        type=str,
        help="AWS account id associated with target profile.",
    )
    args = parser.parse_args()

    load_config("pvdrdb-developer", False)
    quit()
