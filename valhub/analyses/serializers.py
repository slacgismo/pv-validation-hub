from rest_framework import serializers
from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    """
    Serialize the Analysis Model.
    """

    class Meta:
        model = Analysis
        fields = ("analysis_id", "analysis_name", "display_errors")

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["analysis_id"] = instance.analysis_id
    #     return data
