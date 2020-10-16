from django.shortcuts import render
from imports.forms import UserForm, ImportFileForm, ImportFileSet

# Create your views here.


def import_files(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        file_form = ImportFileSet(request.POST, request.FILES)
    else:
        user_form = UserForm()
        file_form = ImportFileSet()
    return render(request, 'imports/imports.html', {'user_form': user_form, 'file_form': file_form})