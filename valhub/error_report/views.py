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
import math
import random


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
