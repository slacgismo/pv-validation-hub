from django.db import models
from submissions.models import Submission


class GracefulErrorReport(models.Model):
    error_id = models.AutoField(primary_key=True)
    submission = models.ForeignKey(
        Submission, related_name="error_reports", on_delete=models.CASCADE
    )
    error_code = models.CharField(max_length=100)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
