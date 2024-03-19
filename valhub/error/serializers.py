from rest_framework import serializers
from .models import GracefulErrorReport


class GracefulErrorReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GracefulErrorReport
        fields = "__all__"
