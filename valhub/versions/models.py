from django.db import models


def default_python_versions():
    return ["3.9", "3.10", "3.11", "3.12"]


class Versions(models.Model):
    python_versions = models.JSONField(
        null=False, blank=False, default=default_python_versions
    )
    old_python_versions = models.JSONField(null=True, blank=True, default=dict)
    cur_worker_version = models.FloatField(null=True, blank=True, default=1.0)
    old_worker_versions = models.JSONField(null=True, blank=True, default=dict)
