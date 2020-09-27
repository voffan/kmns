import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render, reverse
from json import dumps, loads

from reports.views import add_report_data
from users.models import Person
from django.contrib.auth.models import User
from main.models import *
from reports.forms import AddReportForm
from reports.models import *


@login_required(login_url='/users/login/')
@permission_required('reports.delete_report', raise_exception=True)
def delete_report(request, report_id):
    result = {'result': False}
    if request.method == 'POST':
        try:
            instance = Report.objects.get(pk=report_id)
            if instance.state == EDITING or instance.state == NEW:
                result['result'] = True
                result['instance'] = {'id': instance.id, 'user': instance.user.id, 'date': instance.report_date.strftime('%d.%m.%Y'),
                                      'state': instance.state, 'text': instance.text}
                instance.delete()
            else:
                result['error_msg'] = 'Отчет удалить нельзя, т.к. он на согласовании'
        except Exception as e:
            result['error_msg'] = 'Удаляемый отчет не найден!'
    return JsonResponse(result)



@login_required(login_url='/users/login/')
@permission_required('reports.view_report', raise_exception=True)
def get_report(request, report_id):
    result = {'result': False}
    try:
        instance = Report.objects.get(pk=report_id)
        result['result'] = True
        result['instance'] = {'id': instance.id, 'user': instance.user.id, 'date': instance.report_date.strftime('%d.%m.%Y'),
                              'state': instance.state, 'text': instance.text}
    except Exception as e:
        result['error_msg'] = 'Запрашиваемый отчет не найден!'
    return JsonResponse(result)


@login_required(login_url='/users/login/')
@permission_required('reports.change_report', raise_exception=True)
def save_reports(request):
    result = {'result': False}
    if request.method == 'POST':
        if int(request.POST['report_id']) < 0:
            add_form = AddReportForm(request.POST)
        else:
            try:
                add_form = AddReportForm(request.POST, instance=Report.objects.get(pk=request.POST['report_id']))
            except Exception as e:
                result['error_msg'] = 'Редактируемый отчет не найден'
                return JsonResponse(result)
        if add_form.is_valid():
            try:
                with transaction.atomic():
                    instance = add_form.save(commit=True)
                    person = instance.user.person_set.all().first()
                    if person is not None and not person.is_regional and int(request.POST['report_id']) < 0:
                        add_report_data(instance)
                    result['result'] = True
                    result['instance'] = {'id': instance.id, 'user': instance.user.id, 'date': instance.report_date.strftime('%d.%m.%Y'),
                                          'state': instance.state, 'text': instance.text, }
            except Exception as e:
                result['error_msg'] = 'Ошибка при сохранении данных'
        else:
            result['error_msg'] = '<br>'.join([key + ': ' if key != '__all__' else '' + ','.join(value) for key, value in add_form.errors.items()])
    return JsonResponse(result)
