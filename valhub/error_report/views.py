from typing import Any, TypedDict, cast
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from .models import ErrorReport as ErrorReportModel
from .serializers import ErrorReportSerializer, ErrorReportPrivateSerializer
import random
import json
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from pathlib import Path

import logging

from base.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# ...

BASE_DIR = Path(__file__).resolve().parent.parent
error_codes_file = BASE_DIR / "base" / "errorcodes.json"


# Now you can use `error_codes` in your views

VALID_ERROR_PREFIXES = ["op", "wr", "sb"]

UNHANDLED_ERROR_CODES = [400, 500]


def parse_error_code(error_code: str) -> tuple[str, str]:
    error_code = error_code.strip()
    error_code_parts = error_code.split("_")
    if len(error_code_parts) < 2:
        raise ValueError(
            "Error code must have at least 2 parts separated by an underscore"
        )
    prefix = error_code_parts[0]
    if prefix not in VALID_ERROR_PREFIXES:
        raise ValueError(
            f"Error code prefix must be one of {VALID_ERROR_PREFIXES}"
        )
    error_number = error_code_parts[1]
    if not error_number.isdigit():
        raise ValueError("Error number must be a positive integer")

    return prefix, error_number


def get_error_message(error_code: str) -> str:
    prefix, error_number = parse_error_code(error_code)

    logger.info(f"Error code prefix: {prefix}, error number: {error_number}")

    if error_number in UNHANDLED_ERROR_CODES:
        if error_number == 400:
            return "Bad request"
        if error_number == 500:
            return "Internal server error"
        else:
            raise ValueError("Unhandled error code")

    with open(error_codes_file, "r") as f:
        if not f:
            raise ValueError("Error codes file not found")
        error_codes_dict: dict[str, dict[str, str]] = json.load(f)

    if prefix not in error_codes_dict:
        raise ValueError(
            f"Error code prefix '{prefix}' not found in error messages"
        )

    specific_error_codes = error_codes_dict[prefix]

    logger.info(f"Specific error codes: {specific_error_codes}")

    error_message = specific_error_codes.get(error_number)
    if error_message is None:
        raise ValueError(
            f"Error number '{error_number}' not found in error messages"
        )

    return error_message


class ErrorReportList(generics.ListCreateAPIView):
    queryset = ErrorReportModel.objects.all()
    serializer_class = ErrorReportSerializer


class ErrorReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ErrorReportModel.objects.all()
    serializer_class = ErrorReportSerializer


class ErrorReportLeaderboard(generics.ListAPIView):
    #    queryset = ErrorReport.objects.all()
    #    serializer_class = ErrorReportSerializer
    def get_queryset(self):
        #        return ErrorReport.objects.order_by('-score')[:10]
        # Placeholder return value
        return round(random.uniform(1, 100), 2)


@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def ErrorReport(request: Request, *args, **kwargs):
    try:
        request_data = request.data

        if not request_data:
            return JsonResponse(
                {"error": "Request data is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request_data, dict):
            return JsonResponse(
                {"error": "Request data must be a json object"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        modified_data = request_data.copy()

        logger.info(f"Received request data: {modified_data}")

        error_code = modified_data.get("error_code")
        error_rate = modified_data.get("error_rate", None)

        if error_rate is not None:
            modified_data["error_rate"] = error_rate

        if error_code is None:
            return JsonResponse(
                {"error": "error_code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        error_message = get_error_message(error_code)

        modified_data["error_message"] = error_message

        logger.info(f"Modified request data: {modified_data}")

        serializer = ErrorReportSerializer(data=modified_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                serializer.data,
                status=status.HTTP_201_CREATED,
                safe=False,
            )
        else:
            return JsonResponse(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JsonResponse(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ErrorReportPrivateList(request: Request, pk):
    try:
        error_reports = ErrorReportModel.objects.filter(submission=pk)
        serializer = ErrorReportPrivateSerializer(error_reports, many=True)
        return JsonResponse(
            serializer.data, safe=False, status=status.HTTP_200_OK
        )
    except ErrorReportModel.DoesNotExist:
        return JsonResponse(
            {"error": "Error report not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def ErrorReportNew(request: Request):
    # Create a new blank error report

    data = request.data

    serializer = ErrorReportSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(
            serializer.data,
            status=status.HTTP_201_CREATED,
            safe=False,
        )
    else:
        return JsonResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NonBreakingErrorReport(TypedDict):
    error_code: int
    error_type: str
    error_message: str
    file_name: str


@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_non_breaking(request: Request, submission_id: int):

    error_report: ErrorReportModel | None = None

    try:
        error_reports = ErrorReportModel.objects.filter(
            submission=submission_id
        )

        # Get first error report to check if it exists
        error_report = error_reports.first()

        if error_report is None:
            raise ErrorReportModel.DoesNotExist

    except ErrorReportModel.DoesNotExist:
        return JsonResponse(
            {"error": "Error report not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = cast(NonBreakingErrorReport | None, request.data)

    if data is None:
        return JsonResponse(
            {"error": "Request data is empty"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    required_fields = [
        "error_code",
        "error_type",
        "error_message",
        "file_name",
    ]

    for field in required_fields:
        if field not in data:
            return JsonResponse(
                {"error": f"{field} is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    non_breaking_errors: dict[str, Any] = error_report.file_errors

    logger.info(f"Non-breaking errors: {non_breaking_errors}")
    logger.info(type(non_breaking_errors))

    current_errors_list = non_breaking_errors.get("errors", [])
    current_errors_list.append(data)

    non_breaking_errors["errors"] = current_errors_list

    error_report.file_errors = non_breaking_errors

    number_of_non_breaking_errors = len(current_errors_list)

    # Number of files in analysis
    number_of_files_in_task = error_report.submission.analysis.total_files

    # Calculate error rate
    error_rate = number_of_non_breaking_errors / number_of_files_in_task

    error_report.error_rate = error_rate
    error_report.save()

    return JsonResponse(
        {"message": "Non-breaking error added"},
        status=status.HTTP_200_OK,
    )
