# Generated by Django 3.2.16 on 2024-03-27 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('submissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorReport',
            fields=[
                ('error_id', models.AutoField(primary_key=True, serialize=False)),
                ('error_code', models.CharField(max_length=100)),
                ('error_type', models.CharField(max_length=100)),
                ('error_message', models.TextField()),
                ('error_rate', models.FloatField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='error_report', to='submissions.submission')),
            ],
        ),
    ]
