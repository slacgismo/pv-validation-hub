from django.utils.deconstruct import deconstructible
from urllib.parse import urljoin

import os
import uuid
import boto3
import requests
import sys

from datetime import datetime, timedelta
from botocore.signers import CloudFrontSigner
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import base64
import json
import os

def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return 'AWS_EXECUTION_ENV' not in os.environ and 'ECS_CONTAINER_METADATA_URI' not in os.environ and 'ECS_CONTAINER_METADATA_URI_V4' not in os.environ

is_emulation = is_local()


@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        path = self.path
        if "id" in self.path and instance.pk:
            path = self.path.format(id=instance.pk)
        filename = "{}_{}".format(uuid.uuid4(), filename)
        filename = os.path.join(path, filename)
        return filename


# Modify the upload_to_s3_bucket function
def upload_to_s3_bucket(bucket_name, local_path, upload_path):
    if is_emulation:
        upload_path = os.path.join(bucket_name, upload_path)
        s3_file_full_path = 'http://s3:5000/put_object/' + upload_path
        with open(local_path, "rb") as f:
            file_content = f.read()
            r = requests.put(s3_file_full_path, data=file_content)
            if r.status_code != 204:
                print(f"error put file {upload_path} to s3, status code {r.status_code} {r.content}", file=sys.stderr)
                return None
            else:
                return s3_file_full_path.replace('http://s3:5000/put_object/', 'http://s3:5000/get_object/')
    else:
        """Upload file to S3 bucket and return object URL"""
        s3 = boto3.client('s3')

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
    
# Create signed session cookie for S3 directory object
    
def rsa_signer(message):
    with open('/root/.pem/private-key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    signature = private_key.sign(
        message.encode(),  # Encode the message
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    return signature

def create_cloudfront_cookie(directory_path):

        key_id = 'K38U4Q0ELOYHZ1'
        url = 'https://drt7tcx7xxmuz.cloudfront.net' + directory_path
        cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

        # Set an expiration time 1 hour from now
        date_less_than = datetime.utcnow() + timedelta(hours=1)

        # Create signed policy
        policy = cloudfront_signer.build_policy(url, date_less_than=date_less_than)
        print(f"policy: {policy}")

        # Create the signature
        signature = rsa_signer(policy)

        # Create the signed cookies
        signed_cookies = {
            'CloudFront-Policy': base64.b64encode(policy.encode('utf-8')).decode('utf-8'),
            'CloudFront-Signature': base64.b64encode(signature).decode('utf-8'),
            'CloudFront-Key-Pair-Id': key_id
        }

        return signed_cookies
