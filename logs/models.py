from django.db.models import ForeignKey, IntegerField, DateTimeField, CharField
from django.db.models import Model, CASCADE, SET_NULL
from django.contrib.auth.models import User

# Create your models here.

NOACTION = 0
ADD = 1
EDIT = 2
DELETE = 3
UPLOAD = 4
DOWNLOAD = 5

OPERATIONS = (
    (NOACTION, 'Ничего не сделано'),
    (ADD, 'Добавлено'),
    (EDIT, 'Отредактировано'),
    (DELETE, 'Удалено'),
    (UPLOAD, 'Загружено'),
    (DOWNLOAD, 'Выгружено'),
)


class Log(Model):
    class Meta:
        verbose_name = 'Запись в журнал'
        verbose_name_plural = 'Журнал действий'

    parent_object = ForeignKey('contenttypes.ContentType', verbose_name='Объект родитель', related_name='parent_logs', db_index=True, on_delete=CASCADE)
    operation = IntegerField('Операция', choices=OPERATIONS, default=0)
    child_object = ForeignKey('contenttypes.ContentType', verbose_name='Дочерний объект', related_name='child_logs', on_delete=CASCADE)
    log_date = DateTimeField(verbose_name='Дата', auto_now_add=True, db_index=True)
    user_name = CharField('Имя пользователя', max_length=100, blank=True, null=True)
    user = ForeignKey(User, verbose_name='Пользователь', db_index=True, null=True, blank=True, on_delete=SET_NULL)

    def save(self, *args, **kwargs):
        if self.user is not None:
            self.user_name = self.user.username
        super().save(*args, **kwargs)
