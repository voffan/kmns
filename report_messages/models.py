from django.db.models import CharField, ForeignKey, IntegerField, BooleanField, TextField, FloatField, DateField, DateTimeField, AutoField, Field
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Model, CASCADE, SET_NULL
from django.contrib.auth.models import User
from reports.models import Report
from users.models import Person

NORMAL = 1
WARNING = 2
IMPORTANT = 3

TYPES = (
    (NORMAL,    'Нормальное'),
    (WARNING,   'Предупреждение'),
    (IMPORTANT, 'Важное'),
)


class Message(Model):
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    report = ForeignKey(Report, verbose_name='Отчет', db_index=True, on_delete=CASCADE)
    receiver_username = CharField(verbose_name='Имя пользователя получателся', max_length=100)
    receiver = ForeignKey(Person, verbose_name='Адресат', related_name='received_messages', db_index=True, on_delete=CASCADE)
    sender_username = CharField(verbose_name='Имя пользователя получателся', max_length=100)
    sender = ForeignKey(Person, verbose_name='Отправитель', related_name='sent_messages', db_index=True, on_delete=CASCADE)
    message_type = IntegerField(verbose_name='Тип сообщения', choices=TYPES, default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    message_date = DateTimeField(verbose_name='Дата сообщения', auto_now_add=True)
    message_text = CharField(verbose_name='Текст', max_length=512)

    def save(self, *args, **kwargs):
        self.receiver_username = self.receiver.username
        self.sender_username = self.sender.username
        super().save(*args, **kwargs)
