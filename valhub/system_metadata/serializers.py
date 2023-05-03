from rest_framework import serializers
from .models import SystemMetadata

class SystemMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetadata
        fields = '__all__'

