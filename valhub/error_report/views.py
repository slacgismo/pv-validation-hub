from rest_framework import generics
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
    
class ErrorReportPrivateList(generics.ListAPIView):
#    queryset = ErrorReport.objects.all()
#    serializer_class = ErrorReportSerializer
    def get_queryset(self):
#        return ErrorReport.objects.filter(submission__user=self.request.user)
    # Placeholder return value
        return {
                'error_code': 'Error123',
                'error_type': 'TypeError',
                'error_message': 'Data is of the type: NoneType, Expected: int',
                'error_rate': 12.34
            }