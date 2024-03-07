from django.db import models


class ValidationTests(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=128)
    performance_metrics = models.JSONField()
    function_name = models.CharField(max_length=128)

    def __str__(self):
        return self.category_name
