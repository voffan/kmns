from django.db.models import ForeignKey, IntegerField, DateField, CharField
from django.db.models import Model, CASCADE, SET_NULL
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


# Create your models here.

EDITING = 1
READYTOCHECK = 2
CHECKING = 3
ACCEPTED = 4
REWORK = 5
NEW = 6

STATES = (
    (NEW,           'Новый'),
    (EDITING,       'Редактируется'),
    (READYTOCHECK,  'Готов к проверке'),
    (CHECKING,      'Проверяется'),
    (ACCEPTED, 'Согласовано'),
    (REWORK,        'На доработку'),
)


class Report(Model):
    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        unique_together = ['user', 'report_date']

    user = ForeignKey(User, verbose_name='Ответственный', db_index=True, null=True, blank=True, on_delete=SET_NULL)
    state = IntegerField(verbose_name='Состояние', choices=STATES, default=NEW, validators=[MinValueValidator(1), MaxValueValidator(6)])
    date = DateField(verbose_name='Дата добавления', auto_now_add=True)
    report_date = DateField(verbose_name='Дата отчета', db_index=True)
    text = CharField(verbose_name='Комментарии', max_length=250, default='', null=True, blank=True)

    def __str__(self):
        return self.user.username + ': ' + self.report_date.strftime('%d.%m.%Y')

    def change_state(self, new_state):
        pass
