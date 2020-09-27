from collections import defaultdict

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render, reverse
from json import dumps, loads
from main.views import get_table_cells

from main.forms import AddTableForm
from users.models import Person
from main.models import *
import reports.models
from reports.forms import AddReportForm


@login_required(login_url='/users/login/')
@permission_required('reports.view_report', raise_exception=True)
def reports_list(request):
    user_reports = Report.objects.all()
    if request.user.groups.filter(name='Operator').exists():
        user_reports = user_reports.filter(user=request.user)
    users = Person.objects.values_list('user__id', 'fullname')
    form = AddReportForm()
    return render(request, 'reports/reports_list.html', {'reports': user_reports, 'users': users, 'states': reports.models.STATES, 'form': form})


@login_required(login_url='/users/login/')
@permission_required('reports.view_report', raise_exception=True)
def report_data(request, report_id):
    add_form = AddTableForm()
    tables = Table.objects.filter(row__report__id=report_id).distinct()
    tags = get_table_cells(Table.objects.get(name='Группы показателей').id, request.user)
    return render(request, 'main/tables_list.html', {'form': add_form, 'tables': tables, 'tags': tags})


def add_report_data(report):
    person = report.user.person_set.get()
    villages = person.villages.all()
    parameters_list = Cell.objects.filter(Q(col__brief_name__icontains='Название') | Q(col__brief_name__icontains='Группа'),
                                     row__table__name__icontains='Показатели').order_by('row__number', 'col__number')
    parameters = make_dict(parameters_list)
    tables = Table.objects.select_related('tag').filter(tag__isnull=False).order_by('tag__id')
    print(len(tables))
    for i, table in enumerate(tables):
        print(i)
        v_field = table.fields.filter(parent__name__icontains='Наслеги').first()
        p_field = table.fields.filter(parent__name__icontains='Показатели').first()
        o_fields = table.fields.exclude(id__in=([v_field.id] if v_field is not None else []) +
                                               ([p_field.id] if p_field is not None else []))
        for village in villages:
            min_row_number = Row.objects.filter(table__id=table.id).aggregate(Max('number'))['number__max']
            if min_row_number is None:
                min_row_number = 0
            row_number = parameters['count'][table.tag.id] if p_field else 1

            rows_array = [Row(number=i+1, table=table, report=report) for i in range(min_row_number + 1, min_row_number + row_number + 1)]
            Row.objects.bulk_create(rows_array)
            rows = Row.objects.filter(table__id=table.id, number__gt=min_row_number).values_list('id', flat=True)

            #create cellvalues for village
            v_cellvalues_array = [CellValue(ref_value=village) for i in range(row_number)]
            CellValue.objects.bulk_create(v_cellvalues_array)
            last_n = CellValue.objects.filter(cell__value__isnull=True, ref_value__id=village.id).order_by('-id').values_list('id', flat=True)[:row_number]
            v_cellvalues = list(reversed(last_n))

            #create cellvalues for parameters
            p_cellvalues_array = [CellValue(ref_value_id=parameter) for parameter in parameters['data'][table.tag.id]]
            CellValue.objects.bulk_create(p_cellvalues_array)
            last_m = CellValue.objects.filter(cell__value__isnull=True, ref_value__id__in=parameters['data'][table.tag.id]).order_by('-id', 'ref_value__row__number', 'ref_value__col__number').values_list('id', flat=True)[:row_number]
            p_cellvalues = list(reversed(last_m))

            cells = []
            if v_field is not None:
                for j, row in enumerate(rows):
                    cell = Cell()
                    cell.row_id = row
                    cell.col_id = v_field.id
                    cell.value_id = v_cellvalues[j]
                    cells.append(cell)
            if p_field is not None:
                for j, row in enumerate(rows):
                    cell = Cell()
                    cell.row_id = row
                    cell.col_id = p_field.id
                    cell.value_id = p_cellvalues[j]
                    cells.append(cell)
            for row in rows:
                for field in o_fields:
                    cell = Cell()
                    cell.row_id = row
                    cell.col_id = field.id
                    cells.append(cell)
            Cell.objects.bulk_create(cells)
    CellValue.objects.filter(cell__value__isnull=True).delete()


def make_dict(list_values):
    pairs = list(zip(list_values[::2], list_values[1::2]))
    d = {'data':defaultdict(list), 'count':defaultdict(int)}
    for pair in pairs:
        d['data'][pair[0].value.ref_value.id if pair[0].value.ref_value is not None else 0].append(pair[1].id)
        d['count'][pair[0].value.ref_value.id if pair[0].value.ref_value is not None else 0] += 1
    return d