from django.forms import Form, ModelForm, ModelChoiceField, IntegerField, HiddenInput, FileField, TextInput, Select
from main.models import *


class AddTableForm(ModelForm):
    class Meta:
        model = Table
        fields = [
            'id',
            'name',
            'tag'
        ]
        widgets = {
            'id': TextInput(),
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:100%;'}),
            'tag': Select(attrs={'class': 'form-control'}),
        }