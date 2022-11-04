from django.db import models


class Submission:
    submission_id = models.IntegerField(primary_key=True)
