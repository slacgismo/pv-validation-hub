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
        fields = ("evaluation_script", "analysis_name", "description")
