from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    # account = serializers.PrimaryKeyRelatedField(many=True, queryset=Account.objects.all())
    class Meta:
        # model = User
        model = Account
        fields = ('uuid', 'username', 'password', 'firstName', 'lastName', 'email', 'githubLink')
    
    def create(self, validated_data):
        return Account.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.githubLink = validated_data.get('githubLink', instance.githubLink)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
