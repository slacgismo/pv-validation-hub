from django.db import models


class Analysis(models.Model):
    analysis_id = models.IntegerField(primary_key=True)
    evaluation_script = models.FileField()
    annotation_file_name = models.FilePathField(default="test_annotation.txt")
    max_concurrent_submission_evaluation = models.IntegerField(default=100)
