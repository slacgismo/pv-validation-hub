from django.db import models


class Analysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    analysis_name = models.CharField(max_length=100, default="analysis")
    display_errors = models.TextField(null=True, blank=True, default="")


# json array of error fields for FE '[["mae", "MAE"], ["error2", "ERROR"]]'
# keyname, displayname tuple
