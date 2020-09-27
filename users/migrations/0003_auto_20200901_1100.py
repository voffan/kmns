# Generated by Django 3.0.8 on 2020-09-01 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_column_use_in_relation'),
        ('users', '0002_auto_20200806_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='villages',
            field=models.ManyToManyField(blank=True, limit_choices_to={'col__brief_name': 'Название', 'row__table__id': 14}, related_name='users', to='main.Cell', verbose_name='Населенные пункты'),
        ),
    ]
