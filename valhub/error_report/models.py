from django.db import models
from submissions.models import Submission


class ErrorReport(models.Model):
    error_id = models.AutoField(primary_key=True)
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="error_report",
        blank=True,
    )
    # Breaking errors
    error_code = models.CharField(max_length=100, blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(null=True, blank=True)
    # Non breaking errors
    error_rate = models.FloatField(null=True, blank=True)
    file_errors = models.JSONField(blank=True, default=dict)  # type: ignore
