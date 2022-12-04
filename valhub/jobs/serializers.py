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

class SubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serialize the details of Submission Model.
    """
    class Meta:
        model = Submission
        fields = ("submission_id", "algorithm", "analysis_id", "user_id", "result")     
