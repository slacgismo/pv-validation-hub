from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

import os
import json
import boto3
import botocore

from analyses.models import Analysis
from base.utils import upload_to_s3_bucket, get_environment, download_from_s3_bucket
from accounts.models import Account
from .models import Submission

from .serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Submission

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
        # Modify the SQS resource creation
        environment = get_environment()

        if environment == "LOCAL":
            sqs = boto3.resource(
                "sqs",
                endpoint_url="http://sqs:9324",
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            )
        else:
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
            "submission_files", "submission_user_{}.zip".format(user_id), "submission_{}.zip".format(submission_id))
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
            {"analysis_pk": analysis_id, "submission_pk": submission_id})
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
            'result': str(submission.result)
        }
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


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

# Preloader route is not for regular use. It is meant only to create examples quickly for demonstration purposes.
@api_view(["POST"])
@csrf_exempt
def preload_submissions(request):
    data = request.data
    if not isinstance(data, list):
        return JsonResponse({"error": "Invalid data format. Expected a list of submissions."}, status=status.HTTP_400_BAD_REQUEST)

    for submission_data in data:
        analysis_id = submission_data.get('analysis_id')
        user_id = submission_data.get('user_id')

        try:
            analysis = Analysis.objects.get(pk=analysis_id)
            user = Account.objects.get(uuid=user_id)
            
        except (Analysis.DoesNotExist, Account.DoesNotExist):
            continue

        submission = Submission(
            analysis=analysis,
            created_by=user,
            algorithm=submission_data.get('algorithm'),
            mae=submission_data.get('mae'),
            mrt=submission_data.get('mrt'),
            status=Submission.FINISHED,
            data_requirements=submission_data.get('data_requirements').get('data_requirements')
        )
        submission.save()

    return JsonResponse({"message": "Submissions preloaded successfully."}, status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
def get_submission_results(request, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    user_id = submission.created_by.uuid
    bucket_name = "/pv-validation-hub-bucket"
    results_directory = f"submission_files/submission_user_{user_id}/submission_{submission_id}/results/"

    environment = get_environment()
    if environment == "LOCAL":
        storage_endpoint_url = "http://s3:5000/"
    else:
        storage = default_storage

    if environment != "LOCAL":
        _, file_list = storage.listdir(results_directory)
    else:
        local_directory = os.path.join(bucket_name, results_directory)
        file_list = os.listdir(local_directory) if os.path.exists(local_directory) else []

    png_files = [file for file in file_list if file.lower().endswith(".png")]

    if not png_files:
        return JsonResponse({"error": "No .png files found in the results directory"}, status=status.HTTP_404_NOT_FOUND)

    file_urls = []
    for png_file in png_files:
        png_file_path = os.path.join(results_directory, png_file)
        
        if environment == "LOCAL":
            file_url = urljoin(storage_endpoint_url, f"{bucket_name}/{png_file_path}")
        else:
            file_url = download_from_s3_bucket(bucket_name, png_file_path, download_file=False)
        
        if file_url:
            file_urls.append(file_url)
        else:
            return JsonResponse({"error": f"Error retrieving .png file: {png_file}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({"file_urls": file_urls})

@api_view(["GET"])
@csrf_exempt
def get_user_submissions(request, user_id):
    try:
        user = Account.objects.get(uuid=user_id)
    except Account.DoesNotExist:
        response_data = {"error": "User account does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    user_submissions = Submission.objects.filter(created_by=user)
    response_data = SubmissionSerializer(user_submissions, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)
