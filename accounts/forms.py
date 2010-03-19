from django import forms
from django.forms.util import ErrorList
from django.forms import ModelForm
from accounts.models import ACTIVE_CHOICES,TYPE_CHOICES,Users,UserFilters

YES_NO = (
    (0,'YES'),
    (1,'NO'),
)

class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    quarantine_report = forms.BooleanField(required=False)
    noscan = forms.ChoiceField(choices=YES_NO)
    class Meta:
        model = Users

    #def clean(self):
    #    self.cleaned_data = super(UserForm,self).clean()
    #    cleaned_data = self.cleaned_data
    #    password = cleaned_data.get("password")
    #    if password == 'XXXXXXXXXX':
    #        error_msg = u"Provide a password."
    #        self._errors["password"] = ErrorList([error_msg])
    #    return cleaned_data

class StrippedUserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    quarantine_report = forms.BooleanField(required=False)
    noscan = forms.ChoiceField(choices=YES_NO)
    class Meta:
        model = Users
        exclude = ('type','username')

class UserFilterForm(ModelForm):
    class Meta:
        model = UserFilters
