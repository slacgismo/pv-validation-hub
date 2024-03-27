from django.db import models
from submissions.models import Submission


class ErrorReport(models.Model):
    error_id = models.AutoField(primary_key=True)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="error_report"
    )
    error_code = models.CharField(max_length=100)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    error_rate = models.FloatField()
