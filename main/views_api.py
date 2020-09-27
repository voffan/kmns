import math
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect, render, reverse
from main.forms import AddTableForm
from main.models import *
from json import dumps, loads
from users.views import user_can_change
from reports.models import REWORK, EDITING, NEW
from logs.views import get_record, add_log, ADDING, EDITING, DELETION
from main.views import get_table_cells

from users.models import Person


@login_required(login_url='/users/login/')
@permission_required('main.add_table', raise_exception=True)
def table_save(request):
    result = {'result': True}
    operation = ADDING
    if request.method == 'POST':
        if int(request.POST['table_id']) < 0:
            add_form = AddTableForm(request.POST)
        else:
            try:
                add_form = AddTableForm(request.POST, instance=Table.objects.get(pk=request.POST['table_id']))
                operation = EDITING
            except ObjectDoesNotExist:
                result['result'] = False
                result['error_msg'] = 'Редактируемая таблица не найдена!'
                return JsonResponse(result)
        try:
            instance = add_form.save()
            result['instance'] = {'id': instance.id, 'name': instance.name, 'identifier': instance.identifier, 'tag': None, "url": reverse('tables:table_data', args=(instance.id,))}
            if instance.tag:
                result['instance']['tag'] = instance.tag.value.char200_value
            add_log([get_record(request.user, operation, instance, None, None, None)])
        except Exception as e:
            result['result'] = False
            result['error_msg'] = 'Ошибка сохранения данных!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.view_table', raise_exception=True)
def get_table(request, table_id):
    result = {'result': True}
    try:
        table = Table.objects.select_related('tag').get(pk=table_id)
        result['instance'] = {'id': table.id, 'name': table.name, 'identifier': table.identifier, 'tag': None, "url": reverse('tables:table_data', args=(table.id,))}
        if table.tag:
            result['instance']['tag'] = table.tag.value.char200_value
    except Exception as e:
        result['result'] = False
        result['error_msg'] = 'Таблицы с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.delete_table', raise_exception=True)
def delete_table(request, table_id):
    operation = DELETION
    result = {'result': False}
    if request.method == 'POST':
        try:
            table = Table.objects.select_related('tag').get(pk=table_id)
            try:
                with transaction.atomic():
                    result['instance'] = {'id': table.id, 'name': table.name, 'identifier': table.identifier, 'tag': table.tag.value.char200_value if table.tag is not None else None}
                    cells_values = Cell.objects.filter(row__table__id=table_id).values_list('value__id', flat=True)
                    CellValue.objects.filter(id__in=cells_values).delete()
                    table.delete()
                    result['result'] = True
                add_log([get_record(request.user, operation, table, None, None, None)])
            except IntegrityError:
                del result['instance']
                result['error_msg'] = 'Ошибка при удалении таблицы!'
        except ObjectDoesNotExist:
            result['error_msg'] = 'Таблицы с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.add_column', raise_exception=True)
def add_field(request, table_id):
    operation = ADDING
    result = {'result': False}
    if request.method == 'POST':
        table = Table.objects.filter(pk=table_id).first()
        if table is not None:
            field = Column()
            field.full_name = 'Полное название'
            field.brief_name = 'Краткое название'
            field.table = table
            field.parent = None
            field.number = 1
            field.save()
            result['result'] = True
            result['instance'] = {
                                     "id": field.id,
                                     "number": field.number,
                                     "table": field.table.id,
                                     "full_name": field.full_name,
                                     "brief_name": field.brief_name,
                                     "decimal_places": field.decimal_places,
                                     "column_type": field.column_type,
                                     "use_in_relation": field.use_in_relation,
                                     "ref": None
                                    }
            add_log([get_record(request.user, operation, table, field, None, None)])
        else:
            result['error_msg'] = 'Таблицы с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.delete_column', raise_exception=True)
def delete_field(request, field_id):
    operation = DELETION
    result = {'result': False}
    if request.method == 'POST':
        field = Column.objects.select_related('table').filter(pk=field_id).first()
        if field is not None:
            try:
                with transaction.atomic():
                    cells_values = Cell.objects.filter(col__id=field.id).values_list('value__id', flat=True)
                    CellValue.objects.filter(id__in=cells_values).delete()
                    field.delete()
                    result['result'] = True
                add_log([get_record(request.user, operation, field.table, field, None, None)])
            except IntegrityError:
                result['error_msg'] = 'Ошибка при удалении столбца!'
        else:
            result['error_msg'] = 'Столбец с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.change_column', raise_exception=True)
def save_fields(request, table_id):
    operation = EDITING
    records = []
    result = {'result': False}
    if request.method == 'POST':
        table = Table.objects.filter(pk=table_id).first()
        if table is not None:
            try:
                data = loads(request.POST['data'])
                print(data)
                result['data'] = [None]*len(data)
                with transaction.atomic():
                    for i in range(len(data)):
                        field = Column.objects.get(pk=data[i]['id'])
                        field.number = data[i]['number']
                        field.full_name = data[i]['full_name']
                        field.brief_name = data[i]['brief_name']
                        field.column_type = data[i]['column_type']
                        field.decimal_places = data[i]['decimal_places']
                        field.use_in_relation = data[i]["use_in_relation"]
                        if data[i]['ref'] is not None:
                            field.parent = Table.objects.get(pk=data[i]['ref'])
                        field.save()
                        result['data'][i] = {
                                             "id": field.id,
                                             "number": field.number,
                                             "table": field.table.id,
                                             "full_name": field.full_name,
                                             "brief_name": field.brief_name,
                                             "decimal_places": field.decimal_places,
                                             "column_type": field.column_type,
                                             "use_in_relation": field.use_in_relation,
                                             "ref": None,
                                            }
                        records.append(get_record(request.user, operation, table, field, None, None))
                        if field.parent is not None:
                            result['data'][i]['ref'] = field.parent.id
                result['result'] = True
                add_log(records)
            except Exception as e:
                del result['data']
                result['error_msg'] = 'Ошибка при сохранении данных!'
        else:
            result['error_msg'] = 'Таблицы с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.add_cell', raise_exception=True)
def add_row(request, table_id):
    operation = ADDING
    result = {'result': False}
    if request.method == 'POST':
        table = Table.objects.filter(pk=table_id).first()
        if table is not None:
            report = Report.objects.filter(Q(state=EDITING) | Q(state=NEW) | Q(state=REWORK), user=request.user).first()
            if (table.tag is None and request.user.groups.filter(name='Operator').exists()) or \
                    (not request.user.is_superuser and report is None):
                result['error_msg'] = 'Вы не имеете права добавлять данные в эту таблицу!'
                return JsonResponse(result)
            try:
                p = Person.objects.filter(user=request.user).first()
                is_operator = request.user.groups.filter(name='Operator').exists()
                with transaction.atomic():
                    row = Row()
                    row.number = 1
                    row.table = table
                    row.report = report
                    row.save()
                    result['row'] = {'id': row.id, 'number': row.number, 'date': report.id if report is not None else None}
                    for field in table.all_fields.select_related('parent'):
                        cell_value = CellValue()
                        if p is not None and is_operator and field.column_type == REFERENCE and field.parent.id == 14:
                            v_id = p.villages.first().id
                            cell_value.set_value(field.column_type, v_id)
                        cell_value.save()
                        cell = Cell()
                        cell.col = field
                        cell.row = row
                        cell.value = cell_value
                        cell.save()
                        result['row'][cell.col.id] = cell.get_value() if field.column_type!=REFERENCE or cell.get_value() is None else cell.get_value().id
                result['result'] = True
                add_log([get_record(request.user, operation, table, None, row, None)])
            except Exception as e:
                del result['row']
                result['error_msg'] = 'Ошибка при добавлении данных!'
        else:
            result['error_msg'] = 'Таблицы с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.delete_cell', raise_exception=True)
def delete_row(request, row_id):
    operation = DELETION
    result = {'result': False}
    if request.method == 'POST':
        row = Row.objects.select_related('table').filter(pk=row_id).first()
        if row is not None:
            if not user_can_change(row, request.user):
                result['error_msg'] = 'Вы не имеете права удалять данные в этой таблице!'
                return JsonResponse(result)
            try:
                with transaction.atomic():
                    cells_values = Cell.objects.filter(row__id=row.id).values_list('value__id', flat=True)
                    CellValue.objects.filter(id__in=cells_values).delete()
                    row.delete()
                result['result'] = True
                add_log([get_record(request.user, operation, row.table, None, row, None)])
            except Exception as e:
                result['error_msg'] = 'Ошибка при удалении данных!'
        else:
            result['error_msg'] = 'Строки с заданным идентификатором не существует!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.delete_cell', raise_exception=True)
def save_row(request):
    operation = EDITING
    records = []
    result = {'result': False}
    if request.method == 'POST':
        data = loads(request.POST['data'])
        s = ''
        if len(data) > 0:
            row = Row.objects.select_related('table').filter(pk=data[0]['id']).first()
            if not user_can_change(row, request.user):
                result['error_msg'] = 'Вы не имеете права редактировать данные!'
                result['clear'] = True
                return JsonResponse(result)
            fields = row.table.all_fields
        try:
            for row_data in data:
                #узкое место
                row = Row.objects.filter(pk=row_data['id']).first()
                report = Report.objects.filter(pk=row_data['date']).first()
                if row is not None:
                    if not user_can_change(row, request.user):
                        continue
                    with transaction.atomic():
                        row.number = row_data['number']
                        row.report = report
                        row.save()
                        # тут очень плохо!!!! Надо как-то переделать!!!!!! ассоциативный массив????
                        for field in fields:
                            cell = Cell.objects.filter(row__id=row.id, col=field).first()
                            if str(field.id) not in row_data.keys() or (str(field.id) in row_data.keys() and cell is None):
                                cell = Cell()
                                cell.row = row
                                cell.col = field
                                cell.value = CellValue()
                                cell.value.save()
                                cell.save()
                            key = str(field.id)
                            if (field.column_type == INTEGER or field.column_type == FLOAT) and \
                                    row_data[key] is not None and isinstance(row_data[key], str) and\
                                    len(row_data[key]) < 1:
                                row_data[key] = None
                            cell.set_value(row_data[key])
                        '''
                        for key in row_data.keys():
                            if key.isnumeric():
                                cell = Cell.objects.filter(row__id=row.id, col__id=int(key)).first()
                                if cell is not None:
                                    cell.set_value(row_data[key])
                                else:
                                    s += 'Ячейка с идентификатором ' + key + ' не найдена <br>'
                        '''
                    records.append(get_record(request.user, operation, row.table, None, row, None))
                else:
                    s += 'Строка с номером ' + row_data['number'] + ' не найдена <br>'
        except Exception as e:
            s += str(e)
    if len(s) > 0:
        result['error_msg'] = s
        result['result'] = False
    else:
        result['result'] = True
        add_log(records)
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('main.view_cell', raise_exception=True)
def get_table_data(request):
    page = int(request.GET['page'])
    size = int(request.GET['size'])
    data, rows_number = get_table_cells(int(request.GET['table_id']), request.user, page, size)
    result = {
        'last_page': math.ceil(rows_number/size),
        'data': data
    }
    return JsonResponse(result)
