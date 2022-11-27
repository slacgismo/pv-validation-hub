from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)

import os
import json
import boto3
import botocore

from analyses.models import Analysis
from base.utils import upload_to_s3_bucket

from .serializers import SubmissionSerializer

# Create your views here.


@api_view(["POST"])
@csrf_exempt
def analysis_submission(request, analysis_id):
    """API Endpoint for making a submission to a analysis"""
    # check if the analysis exists or not
    # print("analysis_id: {}".format(analysis_id))
    try:
        analysis = Analysis.objects.get(pk=analysis_id)
    except Analysis.DoesNotExist:
        response_data = {"error": "Analysis does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # check if the analysis queue exists or not
    try:
        sqs = boto3.resource(
            "sqs",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        )
        queue_name = "valhub_submission_queue_{}.fifo".format(analysis_id)
        # queue_name = "valhub_submission_queue.fifo"
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        response_data = {"error": "Queue does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # TODO: get user account

    serializer = SubmissionSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(analysis=analysis)
        submission_id = serializer.instance.submission_id
        # print("submission_id: {}".format(submission_id))

        # upload package to s3 and upload evaluation_script_path
        submission_path = serializer.instance.algorithm.path
        # print("submission_path: {}".format(submission_path))
        bucket_name = "pv-insight-application-bucket"
        upload_path = os.path.join(
            "submission_files", "submission_{}.zip".format(submission_id))
        object_url = upload_to_s3_bucket(
            bucket_name, submission_path, upload_path)
        if object_url is None:
            response_data = {"error": "Cannot upload file to S3 bucket"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        # print("object_url: {}".format(object_url))
        serializer.save(algorithm=object_url)

        # send a message to SQS queue
        message = json.dumps(
            {"analysis_pk": analysis_id, "submission_pk": str(submission_id)})
        # print("message: {}".format(message))
        # print("submission_pk: {}".format(json.loads(message)["submission_pk"]))
        response = queue.send_message(
            MessageBody=message, MessageGroupId="1", MessageDeduplicationId=str(submission_id))

        # serializers.serialize('json', [serializer.instance])
        response_data = serializers.serialize('json', [serializer.instance])
    else:
        response_data = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_200_OK)
