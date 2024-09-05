from rest_framework import serializers
from .models import ErrorReport, Submission


class ErrorReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorReport
        fields = "__all__"


class ErrorReportLeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorReport
        fields = ["error_rate"]


class ErrorReportPrivateSerializer(serializers.ModelSerializer):
    data_requirements = serializers.CharField(
        source="submission.data_requirements"
    )
    submitted_at = serializers.DateTimeField(source="submission.submitted_at")
    alt_name = serializers.CharField(source="submission.alt_name")

    class Meta:
        model = ErrorReport
        fields = [
            "error_rate",
            "error_message",
            "error_type",
            "error_code",
            "submission",
            "error_id",
            "data_requirements",
            "submitted_at",
            "alt_name",
        ]
