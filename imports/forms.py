from django.forms import Form, ModelForm, FileInput, IntegerField, NumberInput, FileField, TextInput, Select, formset_factory
from imports.models import ImportTemplate, TemplateIndicators, ImportResult
from main.models import Cell
from users.models import Person


class UserForm(Form):
    users = [(-1, 'Не выбран (Загрузить от имени текущего пользователя)')] + list(Person.objects.values_list('id', 'fullname'))
    user = IntegerField(label='От имени пользователя', required=True, widget=Select(attrs={'class': 'form-control'}, choices=users), initial=-1)


class ImportFileForm(Form):
    tamplates = ImportTemplate.objects.values_list('id', 'name')
    template = IntegerField(label='Шаблон', required=True, widget=Select(attrs={'class': 'form-control'}, choices=tamplates))
    file = FileField(label='Excel-файл', required=True, widget=FileInput())


ImportFileSet = formset_factory(ImportFileForm, max_num=99)


class ImportTemplateForm(ModelForm):
    class Meta:
        model = ImportTemplate
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'})
        }


class TemplateIndicatorsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TemplateIndicatorsForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['indicator'].queryset = Cell.objects.filter(row__table__id=kwargs['initial'].table.id)

    class Meta:
        model = TemplateIndicators
        fields =[
            'table',
            'indicator',
            'col'
        ]
        widgets = {
            'table': Select(attrs={'class': 'form-control'}),
            'indicator': Select(attrs={'class': 'form-control'}),
            'col': NumberInput(attrs={'class': 'form-control'}),
        }