from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    # account = serializers.PrimaryKeyRelatedField(many=True, queryset=Account.objects.all())
    class Meta:
        # model = User
        model = Account
        fields = ('uuid', 'username', 'password', 'passwordSalt', 'passwordHash', 'firstName', 'lastName', 'email', 'githubLink')