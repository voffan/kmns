from django.forms import Form, ModelForm, PasswordInput, EmailInput, TextInput, Select, SelectMultiple
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from users.models import *


class EditPersonForm(ModelForm):
    class Meta:
        model = Person
        fields = [
            'fullname',
            'position',
            'phones',
            #'user__email'
        ]
        widgets = {
            'fullname': TextInput(attrs={'class': 'form-control'}),
            'position': TextInput(attrs={'class': 'form-control'}),
            'phones': TextInput(attrs={'class': 'form-control'}),
        }


class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            #'user__email'
        ]
        widgets = {
            'email': EmailInput(attrs={'class': 'form-control', 'style': 'width:100%;'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = PasswordInput(attrs={'class': 'form-control', 'required': False})
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control', 'required': False})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control', 'required': False})
