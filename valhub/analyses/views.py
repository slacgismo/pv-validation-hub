from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)
from rest_framework.parsers import JSONParser

import boto3
import os

from .models import Analysis
from .serializers import AnalysisSerializer
from base.utils import upload_to_s3_bucket

# Create your views here.


@api_view(["POST"])
@csrf_exempt
def create_analysis(request):
    # TODO: get user account

    serializer = AnalysisSerializer(data=request.data)

    if serializer.is_valid():

        analysis_name = serializer.validated_data["analysis_name"]
        # description = serializer.data["description"]
        # evaluation_script = serializer.data["evaluation_script"]

        serializer.save()
        analysis_id = serializer.instance.analysis_id

        # upload package to s3 and upload evaluation_script_path
        evaluation_script_path = serializer.instance.evaluation_script.path
        # print("evaluation_script_path: {}".format(evaluation_script_path))
        bucket_name = "pv-insight-application-bucket"
        upload_path = os.path.join(
            "evaluation_scripts", "analysis_{}.zip".format(analysis_id))
        object_url = upload_to_s3_bucket(
            bucket_name, evaluation_script_path, upload_path)
        if object_url is None:
            response_data = {"error": "Cannot upload file to S3 bucket"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        # print("object_url: {}".format(object_url))
        serializer.save(evaluation_script=object_url)

        # TODO: create leaderboard

        # spin up a worker instance which would create SQS queue
        ec2 = boto3.resource('ec2')
        worker = ec2.create_instances(
            MinCount=1,
            MaxCount=1,
            LaunchTemplate={
                'LaunchTemplateName': 'pv-insight-worker-template'
            }
        )

        response_data = serializers.serialize('json', [serializer.instance])
    else:
        response_data = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def list_analysis(request):
    analyses = Analysis.objects.all()
    # print(analyses)
    response_data = serializers.serialize('json', analyses)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def analysis_detail(request, analysis_id):
    analysis = Analysis.objects.get(analysis_id=analysis_id)
    # print(analysis)
    response_data = serializers.serialize('json', [analysis])

    return Response(response_data, status=status.HTTP_200_OK)
