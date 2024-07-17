from rest_framework import serializers
from .models import Versions


class VersionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Versions
        fields = "__all__"
