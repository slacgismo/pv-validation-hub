# Generated by Django 3.2.16 on 2024-05-24 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="acceptTerms",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="account",
            name="email",
            field=models.EmailField(max_length=128, unique=True),
        ),
    ]
