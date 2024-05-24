from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
    authentication_classes,
)
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import requests
import os
import json
import boto3
import botocore.exceptions
import logging

from analyses.models import Analysis
from base.utils import upload_to_s3_bucket, is_emulation, create_cloudfront_url
from accounts.models import Account
from .models import Submission
from urllib.parse import urljoin

from .serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Submission

# Create your views here.


def is_local():
    """
    Checks if the application is running locally or in an Amazon ECS environment.

    Returns:
        bool: True if the application is running locally, False otherwise.
    """
    return (
        "AWS_EXECUTION_ENV" not in os.environ
        and "ECS_CONTAINER_METADATA_URI" not in os.environ
        and "ECS_CONTAINER_METADATA_URI_V4" not in os.environ
    )


is_s3_emulation = is_local()


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def analysis_submission(request, analysis_id):
    logging.info(f"request.data = {request.data}")
    """API Endpoint for making a submission to a analysis"""
    # check if the analysis exists or not
    # print("analysis_id: {}".format(analysis_id))
    try:
        analysis = Analysis.objects.get(pk=analysis_id)
    except Analysis.DoesNotExist:
        response_data = {"error": "Analysis does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    logging.info("analysis exists")

    # check if the analysis queue exists or not
    try:
        if is_s3_emulation:
            sqs = boto3.resource(
                "sqs",
                endpoint_url="http://sqs:9324",
                region_name="elasticmq",
                aws_secret_access_key="x",
                aws_access_key_id="x",
                use_ssl=False,
            )
        else:
            sqs = boto3.resource(
                "sqs",
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
            )
        queue_name = "valhub_submission_queue.fifo"
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except botocore.exceptions.ClientError as ex:
        logging.info(f"botocore.exceptions.ClientError = {ex}")
        response_data = {"error": "Queue does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    serializer = SubmissionSerializer(data=request.data)

    if serializer.is_valid():
        logging.info("serializer is valid")
        serializer.save(analysis=analysis, created_by=user)
        submission_id = int(serializer.instance.submission_id)
        # print("submission_id: {}".format(submission_id))

        # upload package to s3 and upload evaluation_script_path
        submission_path = serializer.instance.algorithm.path
        # print("submission_path: {}".format(submission_path))
        bucket_name = "pv-validation-hub-bucket"
        upload_path = os.path.join(
            "submission_files",
            f"submission_user_{user.uuid}",
            f"submission_{submission_id}",
            f"{submission_path.split('/')[-1]}",
        )

        object_url = upload_to_s3_bucket(
            bucket_name, submission_path, upload_path
        )
        if object_url is None:
            response_data = {"error": "Cannot upload file to S3 bucket"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        Submission.objects.filter(submission_id=submission_id).update(
            algorithm_s3_path=object_url, status=Submission.SUBMITTED
        )
        # serializer.save(algorithm=object_url)

        # send a message to SQS queue
        message = json.dumps(
            {
                "analysis_pk": int(analysis_id),
                "submission_pk": int(submission_id),
                "user_pk": int(user.uuid),
                "submission_filename": object_url.split("/")[-1],
            }
        )

        response = queue.send_message(
            MessageBody=message,
            MessageGroupId="1",
            MessageDeduplicationId=str(submission_id),
        )

        # serializers.serialize('json', [serializer.instance])
        # response_data = serializers.serialize('json', [serializer.instance])
        response_data = SubmissionSerializer(serializer.instance).data
    else:
        logging.error("serializer is not valid")
        response_data = serializer.errors
        logging.error(f"serializer.errors = {response_data}")
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submission_detail(request, analysis_id, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    serializer = SubmissionDetailSerializer(
        data={
            "submission_id": str(submission.submission_id),
            "analysis_id": str(submission.analysis.analysis_id),
            "user_id": str(submission.created_by.id),
            "algorithm": str(submission.algorithm),
            "result": str(submission.result),
            "status": str(submission.status),
        }
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_submission_status(request, analysis_id, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    submission.status = request.data["status"]
    try:
        submission.save()
    except ValidationError as e:
        response_data = {"error": "invalid submission status"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    response_data = {
        "success": f"submission {submission_id} status changed to {request.data['status']}"
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_submission_result(request, analysis_id, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    results = request.data
    logging.info(f"results = {results}")
    submission.mae = float(results["mean_mean_absolute_error"])
    submission.mrt = float(results["mean_run_time"])
    submission.data_requirements = results["function_parameters"]
    try:
        submission.save()
    except ValidationError as e:
        response_data = {"error": "invalid submission result"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    response_data = {
        "success": f"submission {submission_id} result changed to {request.data}"
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def user_submission(request: Request, user_id: str):
    """Get all the submissions of a user"""
    # get user account
    try:
        user = Account.objects.get(uuid=user_id)
    except Account.DoesNotExist:
        response_data = {"error": "User account does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    submissions = Submission.objects.filter(created_by=user)
    serializer = SubmissionSerializer(submissions, many=True)

    return Response(serializer.data)
    # response_data = serializers.serialize('json', submissions)
    response_data = SubmissionSerializer(submissions, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def analysis_user_submission(request, analysis_id):
    """Get all the submissions related to a single analysis of a user"""
    # check if the analysis exists or not
    try:
        analysis = Analysis.objects.get(pk=analysis_id)
    except Analysis.DoesNotExist:
        response_data = {"error": "Analysis does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    submissions = Submission.objects.filter(analysis=analysis, created_by=user)
    response_data = SubmissionSerializer(submissions, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["PUT", "POST"])
@csrf_exempt
@parser_classes([JSONParser])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def leaderboard_update(request):
    if request.method in ["PUT", "POST"]:
        submission_id = request.data.get("submission_id")
        mae = request.data.get("mae")
        mrt = request.data.get("mrt")
        data_requirements = request.data.get("data_requirements")

        if not submission_id:
            return Response(
                {"error": "submission_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            submission = Submission.objects.get(submission_id=submission_id)
        except Submission.DoesNotExist:
            return Response(
                {"error": "submission does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

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
        return Response(
            {"error": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


# Preloader route is not for regular use. It is meant only to create examples quickly for demonstration purposes.
@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def preload_submissions(request):
    data = request.data
    if not isinstance(data, list):
        return JsonResponse(
            {"error": "Invalid data format. Expected a list of submissions."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for submission_data in data:
        analysis_id = submission_data.get("analysis_id")
        user_id = submission_data.get("user_id")

        try:
            analysis = Analysis.objects.get(pk=analysis_id)
            user = Account.objects.get(uuid=user_id)

        except (Analysis.DoesNotExist, Account.DoesNotExist):
            continue

        submission = Submission(
            analysis=analysis,
            created_by=user,
            algorithm=submission_data.get("algorithm"),
            mae=submission_data.get("mae"),
            mrt=submission_data.get("mrt"),
            status=Submission.FINISHED,
            data_requirements=submission_data.get("data_requirements").get(
                "data_requirements"
            ),
        )
        submission.save()

    return JsonResponse(
        {"message": "Submissions preloaded successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_submission_results(request, submission_id):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
    except Submission.DoesNotExist:
        response_data = {"error": "submission does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    logging.info(f"start")

    user_id = submission.created_by.uuid
    bucket_name = "pv-validation-hub-bucket"
    results_directory = f"submission_files/submission_user_{user_id}/submission_{submission_id}/results/"
    cf_results_path = (
        f"submission_user_{user_id}/submission_{submission_id}/results/"
    )
    file_urls = []
    ret = {}

    # Update for actual S3 usage as well
    if is_emulation:
        storage_endpoint_url = "http://s3:5000/"
        static_endpoint_url = "http://localhost:5000/"
        directory_url = urljoin(
            storage_endpoint_url, f"{bucket_name}/{results_directory}/list"
        )
        response = requests.get(directory_url)
        if response.status_code != 200:
            return JsonResponse(
                {"error": "Error retrieving results list"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        file_list = response.json()
        base_url = urljoin(
            static_endpoint_url, f"static/{bucket_name}/{results_directory}"
        )
    else:
        # get the list of files in the results directory
        s3 = boto3.client("s3")
        logging.info(f"pre-list_objects_v2")
        response = s3.list_objects_v2(
            Bucket=bucket_name, Prefix=results_directory
        )
        logging.info(f"post-list_objects_v2")
        if "Contents" not in response or not response["Contents"]:
            return JsonResponse(
                {"error": "No files found in the results directory"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # remove the first entry if it is the same as results_directory
        if response["Contents"][0]["Key"] == results_directory:
            file_list = [file["Key"] for file in response["Contents"][1:]]
        else:
            file_list = [file["Key"] for file in response["Contents"]]
        base_url = (
            f"https://{bucket_name}.s3.amazonaws.com/{results_directory}"
        )

    png_files = [file for file in file_list if file.lower().endswith(".png")]
    logging.info(f"png_files: {png_files}")

    if not png_files:
        return JsonResponse(
            {"error": "No .png files found in the results directory"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if is_emulation:
        logging.info(f"emulation: {base_url}")

        for png_file in png_files:
            file_url = urljoin(base_url, png_file)
            if file_url:
                file_urls.append(file_url)
            else:
                return JsonResponse(
                    {"error": f"Error retrieving .png file: {png_file}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    else:
        logging.info(f"not emulation: {cf_results_path}")

        for png_file in png_files:
            file_url = create_cloudfront_url(png_file)
            if file_url:
                file_urls.append(file_url)
            else:
                return JsonResponse(
                    {"error": f"Error retrieving .png file: {png_file}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    # set returns
    logging.info(f"setting returns")
    ret["file_urls"] = file_urls

    return JsonResponse(ret, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_submissions(request, user_id):
    try:
        user = Account.objects.get(uuid=user_id)
    except Account.DoesNotExist:
        response_data = {"error": "User account does not exist"}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    user_submissions = Submission.objects.filter(created_by=user)
    response_data = SubmissionSerializer(user_submissions, many=True).data
    return Response(response_data, status=status.HTTP_200_OK)
