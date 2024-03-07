from django.db import models


class SystemMetadata(models.Model):
    system_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    azimuth = models.FloatField()
    tilt = models.FloatField()
    elevation = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    tracking = models.BooleanField()
    dc_capacity = models.FloatField()

    def __str__(self):
        return self.name
