# Generated by Django 3.2.16 on 2024-08-27 22:32

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
