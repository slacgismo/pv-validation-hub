import hashlib
import boto3
import os

from mypy_boto3_s3 import S3Client


def get_file_hash(file_path: str):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def get_s3_file_hash(
    s3_client: S3Client, bucket_name: str, file_key: str
) -> str:
    s3_file_hash = s3_client.get_object(Bucket=bucket_name, Key=file_key)[
        "ETag"
    ].replace('"', "")
    return s3_file_hash


def get_s3_file_hash_for_list_of_files(
    file_paths: list[str], s3_client: S3Client, bucket_name: str
) -> str:
    hashes: list[str] = []
    for file_key in file_paths:
        s3_file_hash = get_s3_file_hash(s3_client, bucket_name, file_key)
        hashes.append(s3_file_hash)

    combined_hash = combine_hashes(hashes)

    return combined_hash


def get_hash_for_list_of_files(file_paths: list[str]) -> str:
    individual_hashes = [get_file_hash(file_path) for file_path in file_paths]
    combined_hash = combine_hashes(individual_hashes)
    return combined_hash


def are_hashes_the_same(local_hash: str, s3_hash: str) -> bool:
    return local_hash == s3_hash


def combine_hashes(hashes: list[str]) -> str:
    combined_hasher = hashlib.md5()
    for hash in hashes:
        combined_hasher.update(hash.encode())
    return combined_hasher.hexdigest()


if __name__ == "__main__":
    root_folder_path = os.path.dirname(os.path.abspath(__file__))
    data_folder_path = os.path.join(
        root_folder_path, "analysis-tasks/time-shift-detection/data/files"
    )
    test_filename = "4_ac_power__315_15min_full_DST.csv"

    file_path = f"{data_folder_path}/{test_filename}"
    local_file_hash = get_file_hash(file_path)
    print(local_file_hash)

    s3: S3Client = boto3.client("s3")  # type: ignore

    s3_file_hash = get_s3_file_hash(
        s3_client=s3,
        bucket_name="pv-validation-hub-task-data-bucket",
        file_key=f"files/{test_filename}",
    )
    print(s3_file_hash)

    is_same_hash = are_hashes_the_same(local_file_hash, s3_file_hash)
    print(is_same_hash)

    test_filenames = [
        "4_ac_power__315_15min_full_DST.csv",
        "4_ac_power__315_15min.csv",
    ]

    file_paths = [
        file_path
        for file_path in [
            f"{data_folder_path}/{filename}" for filename in test_filenames
        ]
    ]

    local_files_hash = get_hash_for_list_of_files(file_paths)
    print(local_files_hash)

    s3_file_paths = [f"files/{filename}" for filename in test_filenames]

    s3_files_hash = get_s3_file_hash_for_list_of_files(
        s3_file_paths, s3, "pv-validation-hub-task-data-bucket"
    )
    print(s3_files_hash)

    is_same_hash = are_hashes_the_same(local_files_hash, s3_files_hash)
    print(is_same_hash)
