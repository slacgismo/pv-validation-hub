from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)
from django.http import JsonResponse


from .models import Analysis
from submissions.models import Submission
from submissions.serializers import SubmissionDetailSerializer
from .serializers import AnalysisSerializer
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


from base.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Create your views here.


# Public route, leaderboard cards
@api_view(["GET"])
@csrf_exempt
def list_analysis(request: Request):
    analyses = Analysis.objects.all()
    # print(analyses)
    # response_data = serializers.serialize('json', analyses)
    serializer = AnalysisSerializer(analyses, many=True)

    serializer.is_valid(raise_exception=True)

    response_data = serializer.data

    return Response(response_data, status=status.HTTP_200_OK)


# Public route, leaderboard details
@api_view(["GET"])
@csrf_exempt
def analysis_detail(request: Request, analysis_id: str):
    analysis = Analysis.objects.get(analysis_id=analysis_id)

    serializer = AnalysisSerializer(analysis)

    serializer.is_valid(raise_exception=True)

    response_data = serializer.data

    return Response(response_data, status=status.HTTP_200_OK)


# Public Route, leaderboard
@api_view(["GET"])
@csrf_exempt
def leaderboard(request: Request, analysis_id: str):
    analysis = Analysis.objects.get(analysis_id=analysis_id)

    submission_list = Submission.objects.filter(
        analysis=analysis, result__isnull=False, status=Submission.FINISHED
    )
    serializer = SubmissionDetailSerializer(submission_list, many=True)

    serializer.is_valid(raise_exception=True)

    response_data = {"submissions": serializer.data}

    return JsonResponse(response_data, status=status.HTTP_200_OK)


# Update this later to only accept route calls from within 127.0.0.1 or own container
@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_new_analysis(request: Request):
    # Remove user_id related code
    serializer = AnalysisSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    serializer.save()
    response_data = serializer.data
    return Response(response_data, status=status.HTTP_201_CREATED)
