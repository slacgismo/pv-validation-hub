# Generated by Django 3.2.16 on 2024-04-03 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("error_report", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="errorreport",
            name="error_message",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="errorreport",
            name="error_rate",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
