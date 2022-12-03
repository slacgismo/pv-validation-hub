from rest_framework import serializers
from .models import Submission


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
        data["created_by"] = {"id": instance.created_by.id,
                              "username": instance.created_by.username}
        data["result"] = instance.result
        data["status"] = instance.status
        return data
