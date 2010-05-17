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
import re

LIST_OPTIONS = (
  ('1', 'Whitelist'),
  ('2', 'Blacklist'),
)

class UserListAddForm(forms.Form):
    from_address = forms.EmailField(widget=forms.TextInput(attrs={'size':'50'}))
    to_address = forms.EmailField(widget=forms.TextInput(attrs={'size':'50'}))
    list_type = forms.ChoiceField(choices=LIST_OPTIONS)

    def __init__(self, request=None, *args, **kwargs):
        super(UserListAddForm, self).__init__(*args, **kwargs)
        if not request.user.is_superuser:
            user_type = request.session['user_filter']['user_type']
            addresses = request.session['user_filter']['filter_addresses']
            load_addresses = [(request.user.username, request.user.username)]
            if user_type == 'U':
                if addresses:
                    for address in addresses:
                        load_addresses.append((address.filter, address.filter))
            self.fields['to_address'] = forms.ChoiceField(choices=load_addresses)

    def clean_to_address(self):
        to_address = self.cleaned_data['to_address']
        if not email_re.match(to_address):
            raise forms.ValidationError('%s provide a valid e-mail address' % to_address)
        return to_address

class ListAddForm(forms.Form):
    from_address = forms.EmailField(widget=forms.TextInput(attrs={'size':'50'}))
    to_address = forms.CharField(required=False)
    to_domain = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'24'}))
    list_type = forms.ChoiceField(choices=LIST_OPTIONS)

    def __init__(self, request=None, *args, **kwargs):
        super(ListAddForm, self).__init__(*args, **kwargs)
        if not request.user.is_superuser:
            user_type = request.session['user_filter']['user_type']
            addresses = request.session['user_filter']['filter_addresses']
            load_addresses = []
            if user_type == 'D':
                if addresses:
                    for address in addresses:
                        load_addresses.append((address.filter, address.filter))
            self.fields['to_domain'] = forms.ChoiceField(choices=load_addresses)

    def clean_to_address(self):
        to = self.cleaned_data['to_address']
        if to == "" or to is None:
            to = "default"
        else:
            to = to.strip()
            r = re.compile(r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
                r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")', re.IGNORECASE)
            if not r.match(to):
                raise forms.ValidationError('provide a valid user part of the email address')
        return to
    
    def clean_to_domain(self):
        domain = self.cleaned_data['to_domain']
        domain = domain.strip()
       
        if domain != "" and not domain is None:
            r = re.compile(r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)
            if not r.match(domain):
                raise forms.ValidationError('provide a valid domain')
        return domain

    def clean(self):
        cleaned_data = self.cleaned_data
        to_user = cleaned_data.get("to_address")
        to_domain = cleaned_data.get("to_domain")

        if to_user != 'default' and to_domain == '':
            error_msg = u"provide domain name."
            self._errors["to_domain"] = ErrorList([error_msg])
            del cleaned_data["to_domain"]
            del cleaned_data["to_address"]
        return cleaned_data

class ListDeleteForm(forms.Form):
    list_kind = forms.CharField(widget=forms.HiddenInput)
    list_item = forms.CharField(widget=forms.HiddenInput)

class FilterForm(forms.Form):
    query_type = forms.ChoiceField(choices=((1,'containing'),(2,'excluding')))
    search_for = forms.CharField(required=False)
