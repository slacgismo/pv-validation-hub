from django.db import models

from base.utils import RandomFileName
from accounts.models import Account


class Analysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    analysis_name = models.CharField(max_length=100, default="analysis")
    
    evaluation_script = models.FileField(max_length=1000, upload_to=RandomFileName(
        "evaluation_scripts"))  # url to zip file
    # annotation_file_name = models.FilePathField(default="test_annotation.txt", path="")
    max_concurrent_submission_evaluation = models.IntegerField(default=100)
