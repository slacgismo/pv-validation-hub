from django.db import models

from analyses.models import Analysis
from base.utils import RandomFileName
from accounts.models import Account

import uuid


class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    analysis = models.ForeignKey(
        Analysis, related_name="submissions", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        Account, related_name="submission_creator", on_delete=models.CASCADE)
    algorithm = models.FileField(max_length=1000, upload_to=RandomFileName(
        "submission_files"))
    result = models.TextField(null=True, blank=True)
