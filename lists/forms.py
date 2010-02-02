from django import forms
from django.forms.fields import email_re

LIST_OPTIONS = (
  ('1', 'Whitelist'),
  ('2', 'Blacklist'),
)

class ListAddForm(forms.Form):
  to_address = forms.EmailField()
  from_address = forms.CharField()
  list_type = forms.ChoiceField(choices=LIST_OPTIONS)
