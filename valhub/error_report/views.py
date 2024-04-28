from math import e
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from .models import ErrorReport
from .serializers import ErrorReportSerializer
import random
import json
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from pathlib import Path

import logging

# ...

BASE_DIR = Path(__file__).resolve().parent.parent
error_codes_file = BASE_DIR / "base" / "errorcodes.json"


# Now you can use `error_codes` in your views

valid_prefixes = ["op", "wr", "sb"]

unhandled_error_codes = [400, 500]


def parse_error_code(error_code: str) -> tuple[str, str]:
    error_code = error_code.strip()
    error_code_parts = error_code.split("_")
    if len(error_code_parts) < 2:
        raise ValueError(
            "Error code must have at least 2 parts separated by an underscore"
        )
    prefix = error_code_parts[0]
    if prefix not in valid_prefixes:
        raise ValueError(f"Error code prefix must be one of {valid_prefixes}")
    error_number = error_code_parts[1]
    if not error_number.isdigit():
        raise ValueError("Error number must be a positive integer")

    return prefix, error_number


def get_error_message(error_code: str) -> str:
    prefix, error_number = parse_error_code(error_code)

    print(prefix, error_number)

    if error_number in unhandled_error_codes:
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

    print(specific_error_codes)

    error_message = specific_error_codes.get(error_number)
    if error_message is None:
        raise ValueError(
            f"Error number '{error_number}' not found in error messages"
        )

    return error_message


class ErrorReportList(generics.ListCreateAPIView):
    queryset = ErrorReport.objects.all()
    serializer_class = ErrorReportSerializer


class ErrorReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ErrorReport.objects.all()
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
def ErrorReport(request: Request, *args, **kwargs):
    try:
        modified_data = request.data.copy()

        logging.info(f"Received request data: {modified_data}")

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

        logging.info(f"Modified request data: {modified_data}")

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
        logging.error(f"Error processing request: {str(e)}")
        return JsonResponse(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ErrorReportPrivateList(request, pk):
    #    queryset = ErrorReport.objects.all()
    #    serializer_class = ErrorReportSerializer

    #        return ErrorReport.objects.filter(submission__user=self.request.user)
    # Placeholder return value
    ret = {
        "error_code": "Error123",
        "error_type": "TypeError",
        "error_message": "Data is of the type: NoneType, Expected: int",
        "error_rate": 12.34,
    }
    return JsonResponse(ret, status=status.HTTP_200_OK)


# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(["POST"])
@csrf_exempt
def ErrorReportNew(request, pk):
    #    queryset = ErrorReport.objects.all()
    #    serializer_class = ErrorReportSerializer

    #        return ErrorReport.objects.filter(submission__user=self.request.user)
    # Placeholder return value
    ret = {
        "error_code": "Error123",
        "error_type": "TypeError",
        "error_message": "Data is of the type: NoneType, Expected: int",
        "error_rate": 12.34,
    }
    return JsonResponse(ret, status=status.HTTP_200_OK)
