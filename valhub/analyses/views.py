from venv import logger
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
from submissions.models import Submission
from submissions.serializers import SubmissionDetailSerializer
from .serializers import AnalysisSerializer
from base.utils import upload_to_s3_bucket
from accounts.models import Account
from error_report.models import ErrorReport
import logging

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
)


logger = logging.getLogger(__name__)

# Create your views here.


@api_view(["GET"])
@csrf_exempt
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_analysis(request):
    analyses = Analysis.objects.all()
    # print(analyses)
    # response_data = serializers.serialize('json', analyses)
    response_data = AnalysisSerializer(analyses, many=True).data

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def analysis_detail(request, analysis_id):
    analysis = Analysis.objects.get(analysis_id=analysis_id)
    # print(analysis)
    # response_data = serializers.serialize('json', [analysis])
    response_data = AnalysisSerializer(analysis).data

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def leaderboard(request, analysis_id):
    _analysis = Analysis.objects.get(analysis_id=analysis_id)

    if _analysis is None:
        response_data = {"error": "analysis does not exist"}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    submission_list = Submission.objects.filter(
        analysis=_analysis, mae__isnull=False, status=Submission.FINISHED
    )
    serializer = SubmissionDetailSerializer(submission_list, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# Update this later to only accept route calls from within localhost or own container
@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_new_analysis(request):
    # Remove user_id related code
    serializer = AnalysisSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        response_data = serializer.data
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        response_data = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
