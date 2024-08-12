# Generated by Django 3.2.16 on 2024-07-17 23:39

from django.db import migrations, models
import versions.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Versions",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "python_versions",
                    models.JSONField(
                        default=versions.models.default_python_versions
                    ),
                ),
                (
                    "old_python_versions",
                    models.JSONField(blank=True, default=dict, null=True),
                ),
                (
                    "cur_worker_version",
                    models.FloatField(blank=True, default=1.0, null=True),
                ),
                (
                    "old_worker_versions",
                    models.JSONField(blank=True, default=dict, null=True),
                ),
            ],
        ),
    ]