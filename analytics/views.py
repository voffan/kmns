from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from reports.models import Report
from main.models import *


def get_fields(indicators):
    table_fields = dict()
    if 'cell' in indicators.keys():
        fs = Cell.objects.filter(row__table__name='Показатели', id__in=indicators['cell'])
        for f in fs:
            table_fields['c' + str(f.id)] = f.get_value()
    if 'column' in indicators.keys():
        columns = Column.objects.filter(id__in=indicators['column'])#.values_list('row__id', flat=True)
        for column in columns:
            table_fields['f' + str(column.id)] = column.brief_name

    return table_fields


def get_regions_villages():
    regions = Cell.objects.filter(col__brief_name='Район', row__table__name='Наслеги').order_by('row__id').values_list('value__ref_value__value__char200_value', flat=True)
    villages = Cell.objects.filter(col__brief_name='Название', row__table__name='Наслеги').order_by('row__id').values_list('value__char200_value', flat=True)
    return dict(zip(villages, regions))


@login_required(login_url='/users/login/')
@csrf_protect
def index(request):
    all_indicators = Cell.objects.filter(row__table__name='Показатели', col__brief_name='Название').values('id', 'value__char200_value')
    regions = Cell.objects.filter(row__table__name='Районы', col__brief_name='Название').values('id','value__char200_value')
    if request.method == 'POST':
        reports = None
        if 'period' in request.POST:
            reports = Report.objects.filter(id__in=request.POST.getlist('period')).values_list('id', flat=True)
        if reports is None or len(reports) < 1:
            reports = Report.objects.exclude(state=4).order_by('-report_date').values_list('id', flat=True)

        indicators = dict()
        if 'cindicator' in request.POST:
            indicators['cell'] = request.POST.getlist('cindicator')
        if 'findicator' in request.POST:
            indicators['column'] = request.POST.getlist('findicator')

        if 'cell' not in indicators.keys() and 'column' not in indicators.keys():
            raise Http404('Вы не указали показатели!')

        data = dict()
        fields = get_fields(indicators)
        empty_row = fields.copy()
        for key in empty_row.keys():
            empty_row[key] = 0
        #cells = Cell.objects.filter(value__ref_value__id__in=indicators['cell'], row__report__id__in=reports)
        cell_rows = Cell.objects.filter(value__ref_value__id__in=indicators['cell'], row__report__id__in=reports).values_list('row__id', flat=True)
        if 'region' in request.POST and request.POST['region'] != '-1':
            #regions = Cell.objects.filter(id__in=request.POST.getlist('region')).values_list('row__id', flat=True)
            village_rows = Cell.objects.filter(row__table__name='Наслеги', value__ref_value__id__in=request.POST.getlist('region')).values_list('row__id', flat=True)
            villages = Cell.objects.filter(row__id__in=village_rows, col__brief_name='Название').values_list('id', flat=True)
            cell_rows = Cell.objects.filter(row__id__in=cell_rows, value__ref_value__id__in=villages).values_list('row__id', flat=True)

        cells = Cell.objects.filter(
            (Q(col__brief_name='Наслег') | Q(col__brief_name='Значение') | Q(value__ref_value__id__in=indicators['cell'])) &
             Q(row__id__in=cell_rows)).order_by('row__number', 'col__number')
        village_region = get_regions_villages()
        data['Республика Саха (Якутия)'] = empty_row.copy()
        data['Республика Саха (Якутия)']['children'] = {}

        for i in range(0,len(cells),3):
            village = cells[i].get_value().get_value()
            if village_region[village] not in data['Республика Саха (Якутия)']['children'].keys():
                data['Республика Саха (Якутия)']['children'][village_region[village]] = empty_row.copy()
                data['Республика Саха (Якутия)']['children'][village_region[village]]['children'] = {}
            if village not in data['Республика Саха (Якутия)']['children'][village_region[village]]['children'].keys():
                data['Республика Саха (Якутия)']['children'][village_region[village]]['children'][village] = empty_row.copy()
            k = 'c'+str(cells[i+1].get_value().id)
            c = cells[i+2].get_value()
            c = float(c) if type(c)==str and len(c) > 0 else c if type(c) != str else 0
            data['Республика Саха (Якутия)']['children'][village_region[village]]['children'][village][k] += c
            data['Республика Саха (Якутия)']['children'][village_region[village]][k] += c
            data['Республика Саха (Якутия)'][k] += c
        return render(request, "analytics/monitoring.html", {'indicators': all_indicators, 'regions': regions, 'fields': fields, 'data': data})
    return render(request, "analytics/monitoring.html", {'indicators': all_indicators, 'regions': regions})