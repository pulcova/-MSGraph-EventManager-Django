# Generated by Django 4.2.4 on 2023-08-04 08:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='id',
        ),
        migrations.AddField(
            model_name='event',
            name='event_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=200, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
