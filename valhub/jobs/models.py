from django.db import models

from analyses.models import Analysis
from base.utils import RandomFileName

import uuid


class Submission(models.Model):
    submission_id = models.IntegerField(
        primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(
        Analysis, related_name="submissions", on_delete=models.CASCADE
    )
    # TODO
    # created_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    algorithm = models.FileField(max_length=1000, upload_to=RandomFileName(
        "submission_files"))
