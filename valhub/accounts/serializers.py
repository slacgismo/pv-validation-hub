from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    # account = serializers.PrimaryKeyRelatedField(many=True, queryset=Account.objects.all())
    class Meta:
        # model = User
        model = Account
        fields = (
            "uuid",
            "username",
            "password",
            "firstName",
            "lastName",
            "email",
            "acceptTerms",
            "githubLink",
            "webLinks",
        )

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.githubLink = validated_data.get(
            "githubLink", instance.githubLink
        )
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance
