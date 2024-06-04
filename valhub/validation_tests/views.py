from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import ValidationTests
from .serializers import ValidationTestsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

import csv
import io


class ValidationTestsListAPIView(ListAPIView):
    queryset = ValidationTests.objects.all()
    serializer_class = ValidationTestsSerializer


class ValidationTestsDetailAPIView(RetrieveAPIView):
    queryset = ValidationTests.objects.all()
    serializer_class = ValidationTestsSerializer


class ValidationTestsUploadCSV(APIView):
    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response(
                {"detail": "CSV file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        csv_file = request.FILES["file"]
        decoded_file = csv_file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        for row in reader:
            try:
                validation_test = ValidationTests(
                    category_name=row["category_name"],
                    performance_metrics=row["performance_metrics"],
                    function_name=row["function_name"],
                )
                validation_test.full_clean()
                validation_test.save()
            except ValidationError as e:
                return Response(
                    {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"detail": "Validation tests uploaded successfully"},
            status=status.HTTP_201_CREATED,
        )
