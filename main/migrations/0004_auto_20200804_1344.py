# Generated by Django 3.0.8 on 2020-08-04 04:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20200801_1507'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='row',
            name='parent',
        ),
        migrations.AddField(
            model_name='column',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='references', to='main.Table', verbose_name='Таблица'),
        ),
        migrations.AlterField(
            model_name='column',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='main.Table', verbose_name='Таблица'),
        ),
    ]