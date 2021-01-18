from django.db.models import ForeignKey, IntegerField, DateField, CharField, ManyToManyField, DateField
from django.db.models import Model, CASCADE, SET_NULL
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from reports.models import Report
from main.models import *

# Create your models here.

TYPES =(
    (0, 'DEFAULT'),
    (1, 'LIST'),
    (2, 'TABLE'),
)


class ImportTemplate(Model):
    class Meta:
        verbose_name = 'Шаблон импорта данных'
        verbose_name_plural = 'Шаблоны импорта данных'

    name = CharField('Название', max_length=200, db_index=True)
    table = ForeignKey(Table, verbose_name='Таблица', null=True, blank=True, on_delete=CASCADE, limit_choices_to={'tag__isnull': False}, default=1)
    template_type = IntegerField('Тип шаблона', default=0, choices=TYPES)


class ListTemplate(ImportTemplate):
    class Meta:
        verbose_name = 'Шаблон импорта данных списком'
        verbose_name_plural = 'Шаблоны импорта данных списком'

    oktmo_col = IntegerField('Столбец с ОКАТО', default=1, validators=[MinValueValidator(1), MaxValueValidator(10000000)])
    year_col = IntegerField('Столбец периода', default=1, validators=[MinValueValidator(1), MaxValueValidator(16000)])
    indicator_col = IntegerField('Столбец индикаторов', default=1, validators=[MinValueValidator(1), MaxValueValidator(16000)])
    value_col = IntegerField('Столбец значений', default=1, validators=[MinValueValidator(1), MaxValueValidator(16000)])

    def save(self, *args, **kwargs):
        self.template_type = TYPES[1][0]
        super().save(*args, **kwargs)


class TableTemplate(ImportTemplate):
    class Meta:
        verbose_name = 'Шаблон импорта данных из таблицы'
        verbose_name_plural = 'Шаблоны импорта данных из таблицы'

    oktmo = ForeignKey(Cell, verbose_name='Наслег', on_delete=CASCADE, limit_choices_to={'row__table__id': 14, 'col__brief_name': "Название"}, null=True, blank=True)
    year = IntegerField('Период', default=2000, validators=[MinValueValidator(1900), MaxValueValidator(3000)])
    indicator_col = IntegerField('Столбец индикаторов', default=1, validators=[MinValueValidator(1), MaxValueValidator(16000)])
    value_col = IntegerField('Столбец значений', default=1, validators=[MinValueValidator(1), MaxValueValidator(16000)])

    def save(self, *args, **kwargs):
        self.template_type = TYPES[2][0]
        super().save(*args, **kwargs)


class ImportResult(Model):
    class Meta:
        verbose_name = 'Резальтат импорта данных'
        verbose_name_plural = 'резальтаты импорта данных'

    template = ForeignKey(ImportTemplate, verbose_name='Шаблон',  on_delete=CASCADE)
    report_user = ForeignKey(User, verbose_name='Ответственный', on_delete=SET_NULL, related_name='imported_for', null=True, blank=True, default=None)
    upload_user = ForeignKey(User, verbose_name='Загрузил', on_delete=SET_NULL, related_name='imported_by', null=True, blank=True, default=None)
    file_name = CharField('Название файла', max_length=300, null=True, blank=True)
    date = DateField('Дата загрузки', auto_now_add=True)
    result = TextField('Результат',null=True, blank=True)
