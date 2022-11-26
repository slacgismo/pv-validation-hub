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

from .serializers import AnalysisSerializer

# Create your views here.


@api_view(["POST"])
@csrf_exempt
def create_analysis(request):
    serializer = AnalysisSerializer(data=request.data)

    if serializer.is_valid():

        analysis_name = serializer.validated_data["analysis_name"]
        # description = serializer.data["description"]
        # evaluation_script = serializer.data["evaluation_script"]

        # get unique id from analysis name
        analysis_id = int.from_bytes(analysis_name.encode(), 'little')

        serializer.save(analysis_id=analysis_id)
        evaluation_script_path = serializer.instance.evaluation_script.path
        # print("evaluation_script_path: {}".format(evaluation_script_path))

        # upload package to s3 and upload evaluation_script_path
        bucket_name = "pv-insight-application-bucket"
        upload_path = os.path.join(
            "evaluation_scripts", "analysis_{}.zip".format(analysis_id))

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
        )

        s3.upload_file(evaluation_script_path, bucket_name, upload_path)

        bucket_location = boto3.client(
            's3').get_bucket_location(Bucket=bucket_name)
        object_url = "https://{}.s3.{}.amazonaws.com/{}".format(bucket_name,
                                                                bucket_location['LocationConstraint'],
                                                                upload_path)
        # print("object_url: {}".format(object_url))
        serializer.save(evaluation_script=object_url)

        # TODO: create leaderboard

        response_data = serializers.serialize('json', [serializer.instance])
    else:
        response_data = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_200_OK)
