# 
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# vim: ai ts=4 sts=4 et sw=4
#

from django import forms
from baruwa.accounts.models import UserAddresses
from baruwa.config.models import MailHost
from baruwa.utils.regex import HOST_OR_IPV4_RE
from baruwa.config.models import MailAuthHost

class MailHostForm(forms.ModelForm):
    "Mail host add form"
    address = forms.RegexField(regex=HOST_OR_IPV4_RE, 
        widget=forms.TextInput(attrs={'size':'40'}))
    port = forms.CharField(
                    widget=forms.TextInput(attrs={'size':'5', 'value':'25'}))
    useraddress = forms.ModelChoiceField(queryset=UserAddresses.objects.all(), 
        widget=forms.HiddenInput())
    
    class Meta:
        model = MailHost
        exclude = ('id')

class EditMailHost(forms.ModelForm):
    "Edit Mail host form"
    address = forms.RegexField(regex=HOST_OR_IPV4_RE, 
        widget=forms.TextInput(attrs={'size':'40'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'size':'5'}))
    class Meta:
        model = MailHost
        exclude = ('id', 'useraddress')
        
class DeleteMailHost(forms.ModelForm):
    "Delete a mail host form"
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = MailHost
        fields = ('id',)
        
class MailAuthHostForm(forms.ModelForm):
    "Mail auth host add form"
    address = forms.RegexField(regex=HOST_OR_IPV4_RE, 
        widget=forms.TextInput(attrs={'size':'40'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'size':'5'}))
    useraddress = forms.ModelChoiceField(queryset=UserAddresses.objects.all(), 
        widget=forms.HiddenInput())
    class Meta:
        model = MailAuthHost
        
class EditMailAuthHostForm(forms.ModelForm):
    "Edit Mail auth host form"
    address = forms.RegexField(regex=HOST_OR_IPV4_RE, 
        widget=forms.TextInput(attrs={'size':'40'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'size':'5'}))
    class Meta:
        model = MailAuthHost
        exclude = ('id', 'useraddress')
        
class DeleteMailAuthHostForm(forms.ModelForm):
    "Delete a mail auth form"
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = MailAuthHost
        fields = ('id')
        
class InitializeConfigsForm(forms.Form):
    "Initialize a scanning nodes configuration"
    id = forms.CharField(widget=forms.HiddenInput)
        