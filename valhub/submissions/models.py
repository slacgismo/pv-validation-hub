from django.db import models
from django.contrib.postgres.fields import ArrayField

from analyses.models import Analysis
from base.utils import RandomFileName
from accounts.models import Account
from decimal import Decimal

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
        Account, related_name="submission_creator", on_delete=models.CASCADE
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    algorithm = models.FileField(
        max_length=1000, upload_to=RandomFileName("submission_files")
    )
    algorithm_s3_path = models.URLField(max_length=1000)
    result = models.JSONField(null=True, blank=True, default=dict)
    # json object of key/value pairs {"mae": 50, "error2", 5}
    # keyname, error value
    status = models.CharField(
        max_length=30,
        choices=STATUS_OPTIONS,
        db_index=True,
        default=SUBMITTING,
    )
    alt_name = models.TextField(null=True, blank=True, default="")
    # mrt - mean run time
    mrt = models.FloatField(null=True, blank=True)
    data_requirements = ArrayField(
        models.CharField(max_length=100), blank=True, default=list
    )
    archived = models.BooleanField(default=False)
    python_version = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        default="3.11",
    )

    # Fields for calculating the submission progress
    start_time = models.DateTimeField(null=True, blank=True)
    current_file_count = models.IntegerField(null=True, blank=True)
    progress = models.IntegerField(
        null=True, blank=True
    )  # Time in seconds remaining

    worker_version = models.FloatField(null=False, blank=False, default=1.0)
