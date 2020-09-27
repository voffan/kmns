from django.db.models import CharField, ForeignKey, ManyToManyField, BooleanField
from django.db.models import Model, CASCADE, SET_NULL
from django.contrib.auth.models import User
from main.models import Cell

# Create your models here.


class Position(Model):
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    name = CharField(verbose_name='Название должности', max_length=200, db_index=True)


class Person(Model):
    class Meta:
        verbose_name = 'Пользователь системы'
        verbose_name_plural = 'Пользователи системы'

    user = ForeignKey(User, verbose_name='User', db_index=True, null=True, blank=True, on_delete=SET_NULL)
    fullname = CharField(verbose_name='ФИО', max_length=250, db_index=True)
    position = CharField('Должность', max_length=150, null=True, blank=True) #ForeignKey('Position', verbose_name='Должность', null=True, blank=True, on_delete=SET_NULL)
    phones = CharField('Номера контактных телефонов', max_length=100, null=True, blank=True)
    villages = ManyToManyField(Cell, verbose_name='Населенные пункты', related_name='users', blank=True, limit_choices_to={'row__table__id': 14, 'col__brief_name': "Название"})
    is_regional = BooleanField('Главный оператор', default=False, db_index=True)

    def __str__(self):
        return self.fullname


class Operator(Person):
    pass


class Manager(Person):
    pass
