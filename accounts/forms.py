# vim: ai ts=4 sts=4 et sw=4
from django import forms
from django.forms.util import ErrorList
from django.forms import ModelForm
from baruwa.accounts.models import ACTIVE_CHOICES,TYPE_CHOICES,Users,UserFilters

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
