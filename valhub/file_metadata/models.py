from django.db import models
from system_metadata.models import SystemMetadata

class FileMetadata(models.Model):
    file_id = models.AutoField(primary_key=True)
    system_id = models.ForeignKey(SystemMetadata, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=256)
    timezone = models.CharField(max_length=128)
    data_sampling_frequency = models.PositiveIntegerField()
    issue = models.CharField(max_length=256)
    subissue = models.CharField(max_length=256)

    def __str__(self):
        return self.file_name
