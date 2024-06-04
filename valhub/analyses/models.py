from django.db import models


class Analysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    analysis_name = models.CharField(max_length=100, default="analysis")

    max_concurrent_submission_evaluation = models.IntegerField(default=100)
