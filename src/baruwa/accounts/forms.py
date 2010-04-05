#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# vim: ai ts=4 sts=4 et sw=4
from django import forms
from django.forms.util import ErrorList
from django.forms import ModelForm
from django.forms.fields import email_re
from baruwa.accounts.models import ACTIVE_CHOICES,TYPE_CHOICES,Users,UserFilters
import re

YES_NO = (
    (0,'YES'),
    (1,'NO'),
)

Y_N = (
    ('Y','Yes'),
    ('N','No'),
)

class UserForm(ModelForm):
    """
    Generates a form to create user accounts, or update accounts (only full admin)
    """
    password = forms.CharField(widget=forms.PasswordInput)
    quarantine_report = forms.BooleanField(required=False)
    noscan = forms.ChoiceField(choices=YES_NO)
    class Meta:
        model = Users

class StrippedUserForm(ModelForm):
    """
    Generates a form update user accounts
    """
    password = forms.CharField(widget=forms.PasswordInput)
    quarantine_report = forms.BooleanField(required=False)
    noscan = forms.ChoiceField(choices=YES_NO)
    class Meta:
        model = Users
        exclude = ('type','username')

class UserFilterForm(forms.Form):
    """
    Generates a form to create an email user filters
    """
    username = forms.CharField(widget=forms.HiddenInput)
    filter = forms.CharField()
    active = forms.ChoiceField(choices=Y_N)

    def clean_filter(self):
        to = self.cleaned_data['filter']
        if not email_re.match(to.strip()):
            raise forms.ValidationError('%s is not a valid e-mail address.' % to)
        return to

class DomainUserFilterForm(UserFilterForm):
    """
    Generates a form to create a domain user filters
    """
    def clean_filter(self):
        domain = self.cleaned_data['filter']
        domain = domain.strip()
       
        if domain != "" and not domain is None:
            r = re.compile(r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)
            if not r.match(domain):
                raise forms.ValidationError('provide a valid domain')
        return domain
