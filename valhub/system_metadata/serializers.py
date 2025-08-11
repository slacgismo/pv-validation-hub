from rest_framework import serializers
from .models import SystemMetadata


class SystemMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetadata
        fields = [
            "system_id",
            "name",
            "azimuth",
            "tilt",
            "elevation",
            "latitude",
            "longitude",
            "tracking",
            "dc_capacity",
        ]
