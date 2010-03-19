from django import forms
from django.forms.fields import email_re
from accounts.models import ACTIVE_CHOICES,TYPE_CHOICES

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
