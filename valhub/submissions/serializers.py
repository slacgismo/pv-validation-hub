from rest_framework import serializers
from .models import Submission
from analyses.models import Analysis
from accounts.models import Account
from error_report.models import ErrorReport
from error_report.serializers import ErrorReportLeaderboardSerializer
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("uuid", "username")


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ("analysis_id", "analysis_name")


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serialize the Submission Model.
    """

    def __init__(self, *args, **kwargs):
        super(SubmissionSerializer, self).__init__(*args, **kwargs)

    error_rate = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            "algorithm",
            "submission_id",
            "error_rate",
        )

    def get_error_rate(self, obj):
        error_report = ErrorReport.objects.filter(submission=obj).first()
        return (
            error_report.error_rate
            if error_report and error_report.error_rate is not None
            else 0
        )

    def to_representation(self, instance):
        data = super(SubmissionSerializer, self).to_representation(instance)
        data["submission_id"] = instance.submission_id
        data["analysis"] = {
            "analysis_id": instance.analysis.analysis_id,
            "analysis_name": instance.analysis.analysis_name,
        }
        data["created_by"] = {
            "uuid": instance.created_by.uuid,
            "username": instance.created_by.username,
        }
        data["submitted_at"] = instance.submitted_at
        data["result"] = instance.result
        data["status"] = instance.status
        return data


# This is important for the leaderboard
# Let me know if you have issues with this
class SubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serialize the details of Submission Model.
    """

    error_rate = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            "submission_id",
            "algorithm",
            "algorithm_s3_path",
            "analysis_id",
            "result",
            "mae",
            "mrt",
            "data_requirements",
            "error_rate",
        )

    def get_error_rate(self, obj):
        error_report = ErrorReport.objects.filter(submission=obj).first()
        return (
            error_report.error_rate
            if error_report and error_report.error_rate is not None
            else 0
        )

    def to_representation(self, instance):
        data = super(SubmissionDetailSerializer, self).to_representation(
            instance
        )
        data["created_by"] = {
            "uuid": instance.created_by.uuid,
            "username": instance.created_by.username,
        }

        # Attempt to load the stringified array from the text field
        try:
            data_requirements = json.loads(instance.data_requirements)
            # Ensure that the loaded object is a list
            if not isinstance(data_requirements, list):
                raise ValueError(
                    "Loaded object is not a list"
                )  # Include a message with the ValueError
        except (ValueError, TypeError) as e:
            logger.error(
                f"Failed to parse data_requirements for submission {instance.submission_id}: {e}"
            )
            logger.error(f"With a value of {instance.data_requirements}")
            data_requirements = (
                []
            )  # Default to an empty list if any error occurs

        data["data_requirements"] = data_requirements
        return data
