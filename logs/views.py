from django.shortcuts import render
import datetime
from django.conf import settings
import os

# Create your views here.

ADDING = 0
EDITING = 1
DELETION = 2
operations = (
    (ADDING, 'Добавил'),
    (EDITING, 'Отредактировал'),
    (DELETION, 'Удалил'),
)


def add_log(records):
    today = datetime.datetime.today()
    file_name = today.strftime('%d%m%Y') + '.log'
    file_path = os.path.join(settings.BASE_DIR, 'logs', 'files', file_name)
    try:
        with open(file_path, 'a') as log:
            for record in records:
                log.write(record)
    except Exception as e:
        return



def get_record(user, operation, table, field, row, cell):
    try:
        today = datetime.datetime.today().strftime('%d.%m.%Y %H:%M:%S')
        s = today + ' ' + user.username + ' ' + operations[operation][1]
        if row is not None and cell is None:
            s += ' строку #' + str(row.number) + ' в таблице "'
        elif cell is not None and row is not None:
            s += ' значение ' + str(cell.value.get_value()) + ' в строке #' + str(row.number) + ' в таблице "'
        else:
            if field is not None:
                s += ' столбец "' + field.brief_name + '" в '
            s += ' таблицу "'
        s += table.name + '"\n'
    except Exception as e:
        s = 'Для действия' + user.username + ' не было сгенерировано сообщение. ' + str(e) + '\n'
    return s
