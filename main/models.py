from django.db.models import CharField, ForeignKey, IntegerField, BooleanField, TextField, FloatField, DateField, DateTimeField, AutoField, Field
from django.db.models import Model, CASCADE, SET_NULL, Max
from django.core.validators import MaxValueValidator, MinValueValidator
from reports.models import Report
# Create your models here.


BOOLEAN = 1
INTEGER = 2
FLOAT = 3
DATE = 4
DATETIME = 5
TEXT = 6
CHAR50 = 7
CHAR200 = 8
REFERENCE = 9
FORMULA = 10

TYPES = (
    (BOOLEAN, 'Логическое'),
    (INTEGER, 'Целое число'),
    (FLOAT, 'Дробное число'),
    (DATE, 'Краткая дата'),
    (DATETIME, 'Дата'),
    (TEXT, 'Текст'),
    (CHAR50, 'Строка 50 символов'),
    (CHAR200, 'Строка 200 символов'),
    (REFERENCE, 'Ссылка'),
    (FORMULA, 'Формула'),
)


class Tag(Model):
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.name

    name = CharField(verbose_name='Название', max_length=150, db_index=True)


class Table(Model):
    class Meta:
        verbose_name = 'Показатель'
        verbose_name_plural = 'Показатели'

    def __str__(self):
        return self.name

    @property
    def reference_tables(self):
        return Table.objects.filter(id__in=self.fields.filter(column_type=REFERENCE).values_list('table__id', flat=True))

    @property
    def reference_fields(self):
        return self.fields.filter(column_type=REFERENCE).all()

    @property
    def all_fields(self):
        return self.fields.all().order_by('number')

    name = CharField(verbose_name='Название', max_length=150, db_index=True, unique=True)
    identifier = CharField(verbose_name="Идентификатор", max_length=50, db_index=True, blank=True, null=True)
    tag = ForeignKey('Cell', verbose_name='Группа', null=True, blank=True, on_delete=SET_NULL, limit_choices_to={'row__table__name': 'Группы показателей'})#ForeignKey('Tag', verbose_name='Группа', null=True, blank=True, on_delete=SET_NULL)

    def add_empty_row(self):
        pass

    def add_data(self):
        pass


class Row(Model):
    class Meta:
        verbose_name = 'Строка'
        verbose_name_plural = 'Строки'

    def __str__(self):
        return self.table.name + ' ' + str(self.number)

    number = IntegerField(verbose_name="Номер", default=1, validators=[MinValueValidator(1)])
    table = ForeignKey('Table', verbose_name="Таблица", on_delete=CASCADE, db_index=True)
    report = ForeignKey(Report, verbose_name='Отчет', null=True, blank=True, on_delete=SET_NULL, db_index=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            fields = self.table.row_set.all()
            if fields.count() > 0:
                self.number = fields.aggregate(Max('number'))['number__max'] + 1
            else:
                self.number = 1
        super().save(*args, **kwargs)


class Column(Model):
    class Meta:
        verbose_name = 'Столбец'
        verbose_name_plural = 'Столбцы'

    def __str__(self):
        return self.table.name + ' ' + str(self.brief_name)

    number = IntegerField(verbose_name="Номер", default=1, validators=[MinValueValidator(1)])
    table = ForeignKey('Table', verbose_name="Таблица", related_name='fields', on_delete=CASCADE, db_index=True)
    full_name = CharField('Полное наименование', max_length=250)
    brief_name = CharField('Краткое наименование', max_length=50)
    decimal_places = IntegerField('Кол-во знаков после запятой', default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    column_type = IntegerField('Тип', choices=TYPES, default=INTEGER)
    parent = ForeignKey('Table', verbose_name="Таблица", related_name='references', on_delete=SET_NULL, null=True, blank=True, db_index=True)
    use_in_relation = BooleanField(verbose_name="Отображать в связной таблице", default=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            fields = self.table.fields.all()
            if fields.count() > 0:
                self.number = fields.aggregate(Max('number'))['number__max'] + 1
            else:
                self.number = 1
        super().save(*args, **kwargs)


class Cell(Model):
    class Meta:
        verbose_name = 'Ячейка'
        verbose_name_plural = 'Ячейки'
        unique_together = (('col', 'row', ), )

    row = ForeignKey('Row', verbose_name="Строка", on_delete=CASCADE, db_index=True)
    col = ForeignKey('Column', verbose_name="Колонка", on_delete=CASCADE, db_index=True)
    value = ForeignKey('CellValue', verbose_name='Значение', null=True, blank=True, on_delete=SET_NULL)

    def __str__(self):
        if self.row.table.tag is None:
            return str(self.get_value())
        return self.row.table.name + ' R' + str(self.row.number) + ':C' + str(self.col.number) + ' ' + str(self.get_value())

    def get_value(self):
        if self.value is None:
            return ''
        return self.value.get_value(self.col.column_type)

    def set_value(self, new_value):
        if self.value is None:
            self.value = CellValue()
        self.value.set_value(self.col.column_type, new_value)
        self.value.save()


class CellValue(Model):
    class Meta:
        verbose_name = 'Значение ячейки'
        verbose_name_plural = 'Значения ячеек'

    int_value = IntegerField(verbose_name='Значение', null=True, blank=True)
    float_value = FloatField(verbose_name='Значение', null=True, blank=True)
    bool_value = BooleanField(verbose_name='Значение', null=True, blank=True)
    text_value = TextField(verbose_name='Значение', null=True, blank=True)
    char50_value = CharField(verbose_name='Значение', max_length=50, null=True, blank=True)
    char200_value = CharField(verbose_name='Значение', max_length=200, null=True, blank=True)
    date_value = DateField(verbose_name='Значение', null=True, blank=True)
    datetime_value = DateTimeField(verbose_name='Значение', null=True, blank=True)
    ref_value = ForeignKey('Cell', verbose_name='Значение', null=True, blank=True, on_delete=CASCADE)
    formula_value = CharField(verbose_name='Значение', max_length=200, null=True, blank=True)

    def set_value(self, column_type, value):
        if column_type == INTEGER:
            self.int_value = value
        elif column_type == FLOAT:
            self.float_value = value
        elif column_type == BOOLEAN:
            self.bool_value = value
        elif column_type == TEXT:
            self.text_value = value
        elif column_type == CHAR50:
            self.char50_value = value
        elif column_type == CHAR200:
            self.char200_value = value
        elif column_type == DATE:
            self.date_value = value
        elif column_type == DATETIME:
            self.datetime_value = value
        elif column_type == REFERENCE:
            self.ref_value = Cell.objects.filter(pk=value).first()
        elif column_type == FORMULA:
            self.formula_value = value

    def get_value(self, column_type):
        if column_type == INTEGER:
            return self.int_value
        elif column_type == FLOAT:
            return self.float_value
        elif column_type == BOOLEAN:
            return self.bool_value
        elif column_type == TEXT:
            return self.text_value
        elif column_type == CHAR50:
            return self.char50_value
        elif column_type == CHAR200:
            return self.char200_value
        elif column_type == DATE:
            return self.date_value
        elif column_type == DATETIME:
            return self.datetime_value
        elif column_type == REFERENCE:
            return self.ref_value
        elif column_type == FORMULA:
            return self.formula_value