from collections import defaultdict

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import OuterRef, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.shortcuts import redirect, render, reverse, get_object_or_404

from main.models import *
from reports.models import *


def get_fields(indicators):
    table_fields = dict()
    rows_c = Cell.objects.filter(row__table__name='Показатели', col__brief_name='Группа',
                               id__in=indicators['cell']).values_list('row__id', flat=True)
    fs = Cell.objects.filter(row__table__name='Показатели', col__brief_name='Название', row__id__in=rows_c)
    for f in fs:
        table_fields['c' + str(f.id)] = {'brief_name': f.get_value()}

    columns = Column.objects.filter(id__in=indicators['column']).values_list('row__id', flat=True)
    for column in columns:
        table_fields['f' + str(column.id)] = {'brief_name': columns.brief_name}

    return table_fields


def get_regions_villages():
    regions = Cell.objects.filter(col__brief_name='Район', row__table__name='Наслеги').order_by('row__id').values_list('value__ref_value__value__char200_value', flat=True)
    villages = Cell.objects.filter(col__brief_name='Название', row__table__name='Наслеги').order_by('row__id').values_list('value__id', flat=True)
    return dict(zip(villages, regions))


@login_required(login_url='/users/login/')
def get_data(request):
    reports = None
    if 'period' in request.GET:
        reports = Report.objects.filter(id__in=request.GET.getlist('period')).values_list('id', flat=True)
    if reports is None or len(reports) < 1:
        reports = [Report.objects.exclude(state=ACCEPTED).order_by('report_date').id]

    indicators = dict()
    if 'cindicator' in request.GET:
        indicators['cell'] = request.GET.getlist('cindicator')
    if 'findicator' in request.GET:
        indicators['column'] = request.GET.getlist('findicator')

    if len(indicators['cell']) < 1 and len(indicators['column']) < 1:
        raise Http404('Вы не указали группу показателей!')

    data = dict()
    fields = get_fields(indicators)
    empty_row = fields.copy()
    for key in empty_row.keys():
        empty_row[key] = 0
    cells = Cell.objects.filter(value__ref_value__id__in=indicators['cell'], row__report__id__in=reports)
    cell_rows = Cell.objects.filter(value__ref_value__id__in=indicators['cell'], row__report__id__in=reports).values_list('row__id', flat=True)
    if 'region' in request.GET:
        #regions = Cell.objects.filter(id__in=request.GET.getlist('region')).values_list('row__id', flat=True)
        village_rows = Cell.objects.filter(row__table__name='Наслеги', value__ref_value__id__in=request.GET.getlist('region')).values_list('row__id', flat=True)
        villages = Cell.objects.filter(row__id__in=village_rows, col__brief_name='Назание').values_list('id', flat=True)
        cell_rows = cells.filter(value__ref_value__id__in=villages).values_list('row__id', flat=True)

    Cell.objects.filter(
        (Q(col__brief_name='Наслег') | Q(col__brief_name='Значение') | Q(value__ref_value__id__in=indicators['cell'])) &
         Q(row__id__in=cell_rows)).order_by('row__number', 'row__id')
    village_region = get_regions_villages()
    data['Республика Саха (Якутия)'] = empty_row.copy()
    data['Республика Саха (Якутия)']['children'] = []
    row = empty_row.copy()
    region = empty_row.copy()
    row_num = -1

    for i in range(0,len(cells),3):
        if cells[i].row.number != row_num:
            pass
        #if
        k = 'c'+str(cells[i].id)
        c = cells[i].get_value()
        row[k] = c
        data['Республика Саха (Якутия)'][k] += c
        region[k] += c
    return HttpResponse('Here is your data!!')