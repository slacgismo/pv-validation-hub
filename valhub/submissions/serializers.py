from rest_framework import serializers
from .models import Submission
import logging


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serialize the Submission Model.
    """

    def __init__(self, *args, **kwargs):
        super(SubmissionSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Submission
        fields = ("algorithm",)

    def to_representation(self, instance):
        data = super(SubmissionSerializer, self).to_representation(instance)
        data["submission_id"] = instance.submission_id
        data["analysis"] = {"analysis_id": instance.analysis.analysis_id,
                            "analysis_name": instance.analysis.analysis_name}
        data["created_by"] = {"uuid": instance.created_by.uuid,
                            "username": instance.created_by.username}
        data["submitted_at"] = instance.submitted_at
        data["result"] = instance.result
        data["status"] = instance.status
        return data


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serialize the details of Submission Model.
    """
    class Meta:
        model = Submission
        fields = ("submission_id", "algorithm", "algorithm_s3_path", "analysis_id", "result", "mae", "mrt", "data_requirements")

    def to_representation(self, instance):
        data = super(SubmissionDetailSerializer, self).to_representation(instance)
        data["created_by"] = {"uuid": instance.created_by.uuid,
                            "username": instance.created_by.username}
        return data
    
