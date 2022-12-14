from django.db import models
import uuid


class Account(models.Model):
    """
    Model to store a user account
    """
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    email = models.CharField(max_length=100, null=True)
    firstName = models.CharField(max_length=32, null=True)
    lastName = models.CharField(max_length=32, null=True)
    githubLink = models.URLField(max_length=200, null=True, blank=True)
    def __str__(self) -> str:
        return "{}".format(self.username)
    class Meta:
        app_label = "accounts"
        db_table = "user_account"
