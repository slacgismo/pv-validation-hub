from django.db import models

from base.utils import RandomFileName

import uuid


class Analysis(models.Model):
    # analysis_id = models.IntegerField(primary_key=True)
    analysis_id = models.IntegerField(
        primary_key=True, default=uuid.uuid4, editable=False)
    analysis_name = models.CharField(max_length=100, default="analysis")
    description = models.TextField(null=True, blank=True)

    # TODO
    # creator = models.ForeignKey(
    #     "accounts.User",
    #     related_name="analysis_creator",
    #     on_delete=models.CASCADE,
    # )

    evaluation_script = models.FileField(max_length=1000, upload_to=RandomFileName(
        "evaluation_scripts"))  # url to zip file
    annotation_file_name = models.FilePathField(default="test_annotation.txt")
    max_concurrent_submission_evaluation = models.IntegerField(default=100)
