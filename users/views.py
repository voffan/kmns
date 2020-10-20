from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.db import IntegrityError, transaction
from reports.models import *
from main.models import Cell
from users.models import Person
from users.forms import EditUserForm, EditPersonForm, CustomPasswordChangeForm


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('tables:start'))
    if request.method == 'POST':
        args = {}
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('tables:start'))
        else:
            args['login_error'] = "Внимание, вход на сайт не был произведен. " \
                                  "Возможно, вы ввели неверное имя пользователя или пароль."
            return render(request, 'users\login.html', args)
    return render(request, 'users\login.html')


@login_required(login_url='/users/login/')
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('users:login'))


@login_required(login_url='/users/login/')
def user_profile(request):
    person = get_object_or_404(Person, user__id=request.user.id)
    success_message = None
    error_message = None
    if request.method == 'POST':
        form = EditPersonForm(request.POST, instance=person)
        email_form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid() or email_form.is_valid():# or user_form.is_valid():
            try:
                form.save(commit=True)
                email_form.save(commit=True)
                success_message = 'Данные успешно сохранены'
            except:
                error_message = 'Ошибка при сохранении данных'
        else:
            error_message = '<br>'.join([item for key, value in form.errors.items() for item in value]) + '<br>' +\
                            '<br>'.join([item for key, value in email_form.errors.items() for item in value])# + '<br>' +\
                            #'<br>'.join([value for key, value in user_form.errors.items()])
    else:
        form = EditPersonForm(instance=person)
        email_form = EditUserForm(instance=request.user)
    user_form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'users/profile.html', {'form': form, 'email_form': email_form, 'pwd_form': user_form, 'success_message': success_message, 'error_message': error_message})


@login_required(login_url='/users/login/')
def change_password(request):
    person = get_object_or_404(Person, user__id=request.user.id)
    success_message = None
    error_message = None
    if request.method == 'POST':
        pwd_form = CustomPasswordChangeForm(data=request.POST, user=request.user)
        if pwd_form.is_valid():
            try:
                pwd_form.save(commit=True)
                success_message = 'Ваш пароль успешно изменен!'
                update_session_auth_hash(request, pwd_form.user)
            except:
                error_message = 'Ошибка при сохранении данных'
    else:
        pwd_form = CustomPasswordChangeForm(user=request.user)
    form = EditPersonForm(instance=person)
    email_form = EditUserForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form, 'email_form': email_form, 'pwd_form': pwd_form, 'success_message': success_message, 'error_message': error_message})


def user_can_change(row, user):
    p = Person.objects.filter(user=user).first()
    result = user.is_superuser
    if row.table.tag is not None and user.groups.filter(name='Operator').exists():
        c = Cell.objects.filter(row__id=row.id, col__full_name__icontains='наслег',
                                value__ref_value__id__in=p.villages.values_list('id', flat=True))
        result = len(c) > 0
    result = result or (not user.is_superuser and ((row.report is not None) and (row.report.state == EDITING or row.report.state == REWORK or row.report.state == NEW)))
    return result

