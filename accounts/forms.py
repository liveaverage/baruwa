from django import forms
from django.forms import ModelForm
from accounts.models import ACTIVE_CHOICES,TYPE_CHOICES,Users,UserFilters

YES_NO = (
    (0,'YES'),
    (1,'NO'),
)

class AccountAddForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    fullname = forms.CharField()
    type    = forms.ChoiceField(choices=TYPE_CHOICES,initial='U')
    quarantine = forms.BooleanField()
    spamscore = forms.CharField(initial=0)
    highspamscore = forms.CharField(initial=0)
    noscan = forms.ChoiceField(choices=YES_NO)
    quarantine_rcpt = forms.CharField()

class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    quarantine_report = forms.BooleanField(required=False)
    noscan = forms.ChoiceField(choices=YES_NO)
    class Meta:
        model = Users

class UserFilterForm(ModelForm):
    class Meta:
        model = UserFilters
