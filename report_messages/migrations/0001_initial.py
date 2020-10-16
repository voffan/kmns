# Generated by Django 3.0.8 on 2020-07-24 09:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reports', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver_username', models.CharField(max_length=100, verbose_name='Имя пользователя получателся')),
                ('sender_username', models.CharField(max_length=100, verbose_name='Имя пользователя получателся')),
                ('message_type', models.IntegerField(choices=[(1, 'Нормальное'), (2, 'Предупреждение'), (3, 'Важное')], default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)], verbose_name='Тип сообщения')),
                ('message_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата сообщения')),
                ('message_text', models.CharField(max_length=512, verbose_name='Текст')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='users.Person', verbose_name='Адресат')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Report', verbose_name='Отчет')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='users.Person', verbose_name='Отправитель')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
    ]