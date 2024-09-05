# Generated by Django 5.1 on 2024-09-03 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submissions", "0011_alter_submission_progress"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="avg_file_exec_time",
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name="submission",
            name="current_file_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="submission",
            name="progress",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
