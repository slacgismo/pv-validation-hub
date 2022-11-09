from django.db import models


class Submission(models.Model):
    submission_id = models.IntegerField(primary_key=True)
    algorithm = models.FileField()
