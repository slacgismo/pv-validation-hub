from rest_framework import generics
from .models import ErrorReport
from .serializers import ErrorReportSerializer


class ErrorReportList(generics.ListCreateAPIView):
    queryset = ErrorReport.objects.all()
    serializer_class = ErrorReportSerializer


class ErrorReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ErrorReport.objects.all()
    serializer_class = ErrorReportSerializer
