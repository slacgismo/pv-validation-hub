from rest_framework import generics
from .models import GracefulErrorReport
from .serializers import GracefulErrorReportSerializer


class GracefulErrorReportList(generics.ListCreateAPIView):
    queryset = GracefulErrorReport.objects.all()
    serializer_class = GracefulErrorReportSerializer


class GracefulErrorReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GracefulErrorReport.objects.all()
    serializer_class = GracefulErrorReportSerializer
