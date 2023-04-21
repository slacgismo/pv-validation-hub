from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

import os
import json
import boto3
import botocore

from analyses.models import Analysis
from base.utils import upload_to_s3_bucket, get_environment
from accounts.models import Account
from .models import Submission

from .serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Submission

# Create your views here.

is_s3_emulation = True

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
        if is_s3_emulation:
            sqs = boto3.resource(
                "sqs",
                endpoint_url='http://sqs:9324',
                region_name='elasticmq',
                aws_secret_access_key='x',
                aws_access_key_id='x',
                use_ssl=False
            )
        else:
            sqs = boto3.resource(
                "sqs",
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            )
        queue_name = "valhub_submission_queue"
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        response_data = {"error": "Queue does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # get user account
    user_id = request.data["user_id"]
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        response_data = {"error": "User account does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    serializer = SubmissionSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(analysis=analysis, created_by=user)
        submission_id = int(serializer.instance.submission_id)
        # print("submission_id: {}".format(submission_id))

        # upload package to s3 and upload evaluation_script_path
        submission_path = serializer.instance.algorithm.path
        # print("submission_path: {}".format(submission_path))
        bucket_name = "pv-validation-hub-bucket"
        upload_path = os.path.join(
            "submission_files", f"submission_user_{user_id}", f"submission_{submission_id}", f"{submission_path.split('/')[-1]}")
        object_url = upload_to_s3_bucket(
            bucket_name, submission_path, upload_path)
        if object_url is None:
            response_data = {"error": "Cannot upload file to S3 bucket"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        # print("object_url: {}".format(object_url))
        Submission.objects.filter(submission_id=submission_id).update(
            algorithm=object_url, status=Submission.SUBMITTED)
        # serializer.save(algorithm=object_url)

        # send a message to SQS queue
        message = json.dumps(
            {"analysis_pk": int(analysis_id), "submission_pk": int(submission_id), "user_pk": int(user_id)})
        # print("message: {}".format(message))
        # print("submission_pk: {}".format(json.loads(message)["submission_pk"]))
        response = queue.send_message(
            MessageBody=message, MessageGroupId="1", MessageDeduplicationId=str(submission_id))

        # serializers.serialize('json', [serializer.instance])
        # response_data = serializers.serialize('json', [serializer.instance])
        response_data = SubmissionSerializer(serializer.instance).data
    else:
        response_data = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def submission_detail(request, analysis_id, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    serializer = SubmissionDetailSerializer(
        data={
            'submission_id': str(submission.submission_id),
            'analysis_id': str(submission.analysis.analysis_id),
            'user_id': str(submission.created_by.id),
            'algorithm': str(submission.algorithm),
            'result': str(submission.result),
            'status': str(submission.status)
        }
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@csrf_exempt
def change_submission_status(request, analysis_id, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    submission.status = request.data['status']
    try:
        submission.save()
    except ValidationError as e:
        response_data = {"error": "invalid submission status"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    response_data = {"success": f"submission {submission_id} status changed to {request.data['status']}"}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def user_submission(request, user_id):
    # get user account
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        response_data = {"error": "User account does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    submissions = Submission.objects.filter(created_by=user)

    return Response(serializer.data)
    # response_data = serializers.serialize('json', submissions)
    response_data = SubmissionSerializer(submissions, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def analysis_user_submission(request, analysis_id, user_id):
    # check if the analysis exists or not
    try:
        analysis = Analysis.objects.get(pk=analysis_id)
    except Analysis.DoesNotExist:
        response_data = {"error": "Analysis does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # get user account
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        response_data = {"error": "User account does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    submissions = Submission.objects.filter(analysis=analysis, created_by=user)
    # response_data = serializers.serialize('json', submissions)
    response_data = SubmissionSerializer(submissions, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["PUT", "POST"])
@csrf_exempt
@parser_classes([JSONParser])
def leaderboard_update(request):
    if request.method in ["PUT", "POST"]:
        submission_id = request.data.get("submission_id")
        mae = request.data.get("mae")
        mrt = request.data.get("mrt")
        data_requirements = request.data.get("data_requirements")

        if not submission_id:
            return Response({"error": "submission_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = Submission.objects.get(submission_id=submission_id)
        except Submission.DoesNotExist:
            return Response({"error": "submission does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if mae is not None:
            submission.mae = mae

        if mrt is not None:
            submission.mrt = mrt

        if data_requirements is not None:
            submission.data_requirements = data_requirements

        submission.save()

        response_data = SubmissionSerializer(submission).data
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
