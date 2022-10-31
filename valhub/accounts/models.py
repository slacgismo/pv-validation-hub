from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Account(models.Model):
    """
    Model to store a user account
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    githubLink = models.URLField(max_length=200, null=True, blank=True)
    def __str__(self) -> str:
        return "{}".format(self.user)
    class Meta:
        app_label = "accounts"
        db_table = "user_account"
