# Generated by Django 3.2.16 on 2024-09-05 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("error_report", "0003_auto_20240827_1856"),
    ]

    operations = [
        migrations.AddField(
            model_name="errorreport",
            name="file_errors",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
