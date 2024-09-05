from rest_framework import serializers
from .models import Submission
from analyses.models import Analysis
from accounts.models import Account
from error_report.models import ErrorReport
from error_report.serializers import ErrorReportLeaderboardSerializer
from versions.models import Versions
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
    worker_version = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            "algorithm",
            "submission_id",
            "error_rate",
            "alt_name",
            "archived",
            "python_version",
            "worker_version",
        )

    def get_error_rate(self, obj):
        error_report = ErrorReport.objects.filter(submission=obj).first()
        return (
            error_report.error_rate
            if error_report and error_report.error_rate is not None
            else 0
        )

    def get_worker_version(self, obj):
        try:
            version = Versions.objects.get(pk=1)
            return version.cur_worker_version
        except Versions.DoesNotExist:
            return None

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
        data["alt_name"] = instance.alt_name
        data["archived"] = instance.archived
        data["python_version"] = instance.python_version
        data["worker_version"] = instance.worker_version

        # Update worker_version to use the value from Versions model with PK 1
        try:
            version = Versions.objects.get(pk=1)
            data["worker_version"] = version.cur_worker_version
        except Versions.DoesNotExist:
            data["worker_version"] = None

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
            "mrt",
            "data_requirements",
            "error_rate",
            "submitted_at",
            "alt_name",
            "archived",
            "python_version",
            "worker_version",
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

        return data


class SubmissionPrivateReportSerializer(serializers.ModelSerializer):
    """
    Serialize the private report of Submission Model.
    """

    class Meta:
        model = Submission
        fields = (
            "submission_id",
            "result",
            "mrt",
            "data_requirements",
            "submitted_at",
            "alt_name",
            "archived",
            "python_version",
            "worker_version",
            "status",
        )

    def to_representation(self, instance):
        data = super(
            SubmissionPrivateReportSerializer, self
        ).to_representation(instance)
        data["created_by"] = {
            "uuid": instance.created_by.uuid,
            "username": instance.created_by.username,
        }

        return data
