import os

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView
from imports.forms import UserForm, ImportFileForm, ImportFileSet
from imports.impexcel import import_excel
from imports.models import *
from django.contrib.auth.models import User

# Create your views here.


def process_file(filename, file):
    s = os.path.join(settings.BASE_DIR, 'uploads', filename)
    with open(s, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


@login_required(login_url='/users/login/')
@permission_required('main.add_cell', raise_exception=True)
def import_files(request):
    if request.method == 'POST':
        file_form = ImportFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            process_file(request.FILES['file'].name, request.FILES['file'])
            result = import_excel(file_form.cleaned_data['template'], file_form.cleaned_data['file'].name, request.user)
            return redirect(reverse('imports:importresult', kwargs={'result_id': result.id}))
    else:
        file_form = ImportFileForm()
    return render(request, 'imports/import_wb.html', {'file_form': file_form})


class ImportResultDetailView(DetailView):
    model = ImportResult
    template_name = 'imports/results.html'
    pk_url_kwarg = 'result_id'
