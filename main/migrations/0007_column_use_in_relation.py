# Generated by Django 3.0.8 on 2020-09-01 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20200808_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='use_in_relation',
            field=models.BooleanField(default=False, verbose_name='Отображать в связной таблице'),
        ),
    ]
