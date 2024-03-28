from rest_framework import serializers
from .models import ErrorReport


class ErrorReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorReport
        fields = "__all__"


class ErrorReportLeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorReport
        fields = ["error_rate"]
