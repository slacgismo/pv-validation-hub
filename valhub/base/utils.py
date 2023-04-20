from django.utils.deconstruct import deconstructible

import os
import uuid
import boto3
import requests
import sys

is_s3_emulation = True

@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        extension = os.path.splitext(filename)[1]
        path = self.path
        if "id" in self.path and instance.pk:
            path = self.path.format(id=instance.pk)
        filename = "{}{}".format(uuid.uuid4(), extension)
        filename = os.path.join(path, filename)
        return filename


def upload_to_s3_bucket(bucket_name, local_path, upload_path):
    if is_s3_emulation:
        upload_path = os.path.join(bucket_name, upload_path)
        s3_file_full_path = 'http://s3:5000/' + upload_path
        with open(local_path, "rb") as f:
            file_content = f.read()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                print(f"error put file {upload_path} to s3, status code {r.status_code} {r.content}", file=sys.stderr)
                return None
            else:
                return s3_file_full_path
    else:
        """Upload file to S3 bucket and return object URL"""
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
        )

        try:
            s3.upload_file(local_path, bucket_name, upload_path)
        except:
            return None

        bucket_location = boto3.client(
            's3').get_bucket_location(Bucket=bucket_name)
        object_url = "https://{}.s3.{}.amazonaws.com/{}".format(bucket_name,
                                                                bucket_location['LocationConstraint'],
                                                                upload_path)
        return object_url
