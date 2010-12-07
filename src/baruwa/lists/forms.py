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
from django.template.defaultfilters import force_escape
from django.utils.translation import ugettext_lazy as _
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re
from baruwa.utils.regex import DOM_RE, IPV4_RE, USER_RE, IPV4_NET_OR_RANGE_RE

LIST_TYPES = (
    ('1', 'Whitelist'),
    ('2', 'Blacklist'),
)

class ListAddForm(forms.Form):
    """ListAddForm"""

    list_type = forms.ChoiceField(choices = LIST_TYPES)
    from_address = forms.CharField(widget = forms.TextInput(
        attrs = {'size':'50'}))
    to_address = forms.CharField(required=False)

    def __init__(self, request=None, *args, **kwargs):
        super(ListAddForm, self).__init__(*args, **kwargs)
        self.request = request
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            load_addresses = [(address, address) for address in addresses]
            self.fields['to_address'] = forms.ChoiceField(
                choices=load_addresses)

    def clean_to_address(self):
        to_address = self.cleaned_data['to_address']
        if not email_re.match(to_address):
            raise forms.ValidationError(
                _('%(email)s provide a valid e-mail address') % 
                {'email':force_escape(to_address)})
        if to_address not in self.request.session['user_filter']['addresses'] \
            and not self.request.user.is_superuser():
            raise forms.ValidationError(
                _("The address: %(email)s does not belong to you.") % 
                {'email':force_escape(to_address)})
        return to_address

    def clean_from_address(self):
        from_address = self.cleaned_data['from_address']
        from_address = from_address.strip()

        if (not email_re.match(from_address) and not DOM_RE.match(from_address)
                and not IPV4_RE.match(from_address) and not
                IPV4_NET_OR_RANGE_RE.match(from_address)):
            raise forms.ValidationError(_("Provide either a valid IPv4, email,"
            " Domain address, or IPv4 network or range"))
        return from_address

    def clean(self):
        "check for duplicates, implemented coz of mysql utf8 bug"
        cleaned_data = self.cleaned_data
        from_address = cleaned_data.get("from_address")
        to_address = cleaned_data.get("to_address")
        from baruwa.lists.models import List
        list_objs = List.objects.filter(from_address = from_address,
        to_address = to_address)
        if list_objs:
            raise forms.ValidationError(_("The list item already exists"))
        return cleaned_data

class AdminListAddForm(ListAddForm):
    """AdminListAddForm"""

    user_part = forms.CharField(required = False)
    def __init__(self, *args, **kwargs):
        super(AdminListAddForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            addresses = self.request.session['user_filter']['addresses']
            load_addresses = [(address, address) for address in addresses]
            self.fields['to_address'] = forms.ChoiceField(
            choices = load_addresses)
        else:
            self.fields['to_address'].widget = forms.TextInput(
            attrs = {'size':'24'})

    def clean_to_address(self):
        """clean_to_address"""
        to_address = self.cleaned_data['to_address']
        try:
            to_address = to_address.strip()
        except:
            pass
        if not self.request.user.is_superuser:
            addresses = self.request.session['user_filter']['addresses']
            if to_address not in addresses:
                raise forms.ValidationError(
                _("The address: %(addr)s does not belong to you.") 
                % {'addr':force_escape(to_address)})

        if to_address != "" and not to_address is None:
            if not DOM_RE.match(to_address):
                raise forms.ValidationError(_("Provide either a valid domain"))
        else:
            to_address = 'any'

        return to_address

    def clean_user_part(self):
        """clean_user_part"""
        user_part = self.cleaned_data['user_part']

        if user_part == '' or user_part is None:
            user_part = 'any'
        else:
            user_part = user_part.strip()
            if not USER_RE.match(user_part):
                raise forms.ValidationError(
                _('provide a valid user part of the email address'))
        return user_part

class FilterForm(forms.Form):
    query_type = forms.ChoiceField(
        choices = ((1, 'containing'), (2, 'excluding')))
    search_for = forms.CharField(required = False)

class ListDeleteForm(forms.Form):
    list_item = forms.CharField(widget = forms.HiddenInput)
