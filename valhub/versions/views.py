from typing import Any, cast
from venv import logger
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, generics
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
    authentication_classes,
)
from rest_framework.parsers import JSONParser
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

import requests
import os
import json
import logging

from .models import Versions
from .serializers import VersionsSerializer


logger = logging.getLogger(__name__)

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


class VersionsListCreateView(generics.ListCreateAPIView):
    queryset = Versions.objects.all()
    serializer_class = VersionsSerializer


class VersionsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Versions.objects.all()
    serializer_class = VersionsSerializer


@csrf_exempt
@api_view(["GET"])
def GetPythonVersions(request):
    try:
        version = Versions.objects.get(pk=1)
        python_versions = list(version.python_versions)
        return JsonResponse(python_versions, safe=False)
    except Versions.DoesNotExist:
        return JsonResponse(
            {"error": "No versions found with ID 1"}, status=404
        )
