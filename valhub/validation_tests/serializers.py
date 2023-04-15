from rest_framework import serializers
from .models import ValidationTests


class ValidationTestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationTests
        fields = '__all__'
