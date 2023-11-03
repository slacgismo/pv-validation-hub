from rest_framework import serializers
from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    """
    Serialize the Analysis Model.
    """

    def __init__(self, *args, **kwargs):
        super(AnalysisSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Analysis
        fields = ("analysis_name")

    def to_representation(self, instance):
        data = super(AnalysisSerializer, self).to_representation(instance)
        data["analysis_id"] = instance.analysis_id
        data["analysis_name"] = instance.analysis_name
        return data
