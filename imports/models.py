from django.db.models import ForeignKey, IntegerField, DateField, CharField, ManyToManyField, DateField
from django.db.models import Model, CASCADE, SET_NULL
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from reports.models import Report
from main.models import *

# Create your models here.


class ImportTemplate(Model):
    class Meta:
        verbose_name = 'Шаблон импорт данных'
        verbose_name_plural = 'Шаблоны импорт данных'
    name = CharField('Название', max_length=200, db_index=True)


class TemplateIndicators(Model):
    class Meta:
        verbose_name = 'Настройка индикаторов'
        verbose_name_plural = 'Настройки индикаторов'

    template = ForeignKey(ImportTemplate, verbose_name='Настройки', on_delete=CASCADE)
    table = ForeignKey(Table, verbose_name='Таблица', on_delete=CASCADE, limit_choices_to={'tag__isnull': False})
    indicator = ForeignKey(Cell, verbose_name='Показатель', on_delete=CASCADE)
    col = IntegerField('Столбец', default=1, validators=[MinValueValidator(1), MaxValueValidator(16000)])


class ImportResult(Model):
    class Meta:
        verbose_name = 'Резальтат импорта данных'
        verbose_name_plural = 'резальтаты импорта данных'

    template = ForeignKey(ImportTemplate, verbose_name='Настройки', on_delete=CASCADE)
    report_user = ForeignKey(User, verbose_name='Ответственный', on_delete=SET_NULL, related_name='imported_for', null=True, blank=True, default=None)
    upload_user = ForeignKey(User, verbose_name='Загрузил', on_delete=SET_NULL, related_name='imported_by', null=True, blank=True, default=None)
    file_name = CharField('Название файла', max_length=300, null=True, blank=True)
    date = DateField('Дата загрузки', auto_now_add=True)
    result = TextField('Результат',null=True, blank=True)
