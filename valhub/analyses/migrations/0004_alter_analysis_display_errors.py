# Generated by Django 3.2.16 on 2024-07-17 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analyses", "0003_rename_result_analysis_display_errors"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysis",
            name="display_errors",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]