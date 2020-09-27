# Generated by Django 3.1.1 on 2020-09-21 12:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0008_auto_20200921_2101'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='report',
            unique_together={('user', 'report_date')},
        ),
    ]
