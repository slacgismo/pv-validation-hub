from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    """
    Model to store a user account
    """

    uuid = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=32, null=True)
    lastName = models.CharField(max_length=32, null=True)
    email = models.EmailField(max_length=128, unique=True)
    acceptTerms = models.BooleanField(default=False)
    githubLink = models.URLField(max_length=200, blank=True)
    webLinks = models.JSONField(default=dict, blank=True)
    organization = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=64, blank=True)
    profileImage = models.CharField(max_length=64, default="ducky.jpg")

    def __str__(self) -> str:
        return self.username

    class Meta:
        app_label = "accounts"
        db_table = "user_account"
