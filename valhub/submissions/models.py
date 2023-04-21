from django.db import models

from analyses.models import Analysis
from base.utils import RandomFileName
from accounts.models import Account

import uuid


class Submission(models.Model):
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    RUNNING = "running"
    FAILED = "failed"
    FINISHED = "finished"

    STATUS_OPTIONS = (
        (SUBMITTED, SUBMITTED),
        (RUNNING, RUNNING),
        (FAILED, FAILED),
        (FINISHED, FINISHED),
        (SUBMITTING, SUBMITTING),
    )

    submission_id = models.AutoField(primary_key=True)
    analysis = models.ForeignKey(
        Analysis, related_name="submissions", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        Account, related_name="submission_creator", on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    algorithm = models.FileField(max_length=1000, upload_to=RandomFileName(
        "submission_files"))
    result = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=30, choices=STATUS_OPTIONS, db_index=True, default=SUBMITTING)

    # mae - mean average error 
    # mrt - mean run time

    mae = models.FloatField(null=True, blank=True)
    mrt = models.FloatField(null=True, blank=True)
    data_requirements = models.JSONField(null=True, blank=True)
