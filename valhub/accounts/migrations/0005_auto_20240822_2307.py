# Generated by Django 3.2.16 on 2024-08-22 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_account_weblinks"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="organization",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="account",
            name="title",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]