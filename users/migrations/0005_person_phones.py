# Generated by Django 3.0.8 on 2020-09-17 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_person_is_regional'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='phones',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Номера контактных телефонов'),
        ),
    ]