# Generated by Django 5.1 on 2024-08-27 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analyses", "0004_alter_analysis_display_errors"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysis",
            name="total_files",
            field=models.IntegerField(default=1),
        ),
    ]
