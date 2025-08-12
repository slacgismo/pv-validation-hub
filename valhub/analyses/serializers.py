from rest_framework import serializers
from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    """
    Serialize the Analysis Model.
    """

    class Meta:
        model = Analysis
        fields = [
            "analysis_id",
            "analysis_name",
            "display_errors",
            "total_files",
            "hash",
            "version",
        ]
