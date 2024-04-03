from math import e
from rest_framework import generics
from .models import ErrorReport
from .serializers import ErrorReportSerializer
import random
import json
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from pathlib import Path

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

    def post(self, request: Request, *args, **kwargs):
        # Custom POST logic here
        # ...
        try:
            modified_data = request.data.copy()

            error_code = modified_data.get("error_code")
            error_rate = modified_data.get("error_rate", None)

            if error_rate is not None:
                modified_data["error_rate"] = error_rate

            if error_code is None:
                return Response(
                    {"error": "error_code is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            error_message = get_error_message(error_code)

            modified_data["error_message"] = error_message

            print(modified_data)

            serializer = self.get_serializer(data=modified_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


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


class ErrorReportPrivateList(generics.ListAPIView):
    #    queryset = ErrorReport.objects.all()
    #    serializer_class = ErrorReportSerializer
    def get_queryset(self):
        #        return ErrorReport.objects.filter(submission__user=self.request.user)
        # Placeholder return value
        return {
            "error_code": "Error123",
            "error_type": "TypeError",
            "error_message": "Data is of the type: NoneType, Expected: int",
            "error_rate": 12.34,
        }
