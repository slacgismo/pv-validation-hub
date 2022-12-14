from django.db import models

from base.utils import RandomFileName
from accounts.models import Account

import uuid


class Analysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    analysis_name = models.CharField(max_length=100, default="analysis")
    
    description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    ruleset = models.TextField(null=True, blank=True)
    dataset_description = models.TextField(null=True, blank=True)

    creator = models.ForeignKey(
        Account,
        related_name="analysis_creator",
        on_delete=models.CASCADE,
    )

    evaluation_script = models.FileField(max_length=1000, upload_to=RandomFileName(
        "evaluation_scripts"))  # url to zip file
    annotation_file_name = models.FilePathField(default="test_annotation.txt")
    max_concurrent_submission_evaluation = models.IntegerField(default=100)
