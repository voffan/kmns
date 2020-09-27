from django.forms import Form, ModelForm, ModelChoiceField, DateInput, HiddenInput, DateTimeInput, TextInput, Select, Textarea
from reports.models import *


class AddReportForm(ModelForm):
    class Meta:
        model = Report
        fields = [
            'id',
            'user',
            'state',
            'report_date',
            'text'
        ]
        widgets = {
            'id': HiddenInput(),
            'user': Select(attrs={'class': 'form-control', 'placeholder': 'Выберите ответственного'}),
            'state': Select(attrs={'class': 'form-control', 'placeholder': 'Выберите состояние'}),
            'report_date': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format=('%d.%m.%Y')),
            'text': Textarea(attrs={'class': 'form-control', 'style': 'width:100%;', 'rows': 4}),
        }