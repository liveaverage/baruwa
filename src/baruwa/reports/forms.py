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
from baruwa.utils.regex import DOM_RE
import datetime, time
try:
    from django.forms.fields import email_re
    from django.forms.fields import ipv4_re
except ImportError:
    from django.core.validators import email_re
    from django.core.validators import ipv4_re


FILTER_ITEMS = (
    ('id','Message ID'),
    ('size','Size'),
    ('from_address','From Address'),
    ('from_domain', 'From Domain'),
    ('to_address','To Address'),
    ('to_domain','To Domain'),
    ('subject','Subject'),
    ('clientip','Received from'),
#    ('archive','Is Archived'),
    ('scaned', 'Was scanned'),
    ('spam','Is spam'),
    ('highspam','Is high spam'),
    ('saspam','Is SA spam'),
    ('rblspam','Is RBL listed'),
    ('whitelisted','Is whitelisted'),
    ('blacklisted','Is blacklisted'),
    ('sascore','SA score'),
    ('spamreport','Spam report'),
    ('virusinfected','Is virus infected'),
    ('nameinfected','Is name infected'),
    ('otherinfected','Is other infected'),
    ('date','Date'),
    ('time','Time'),
    ('headers','Headers'),
    ('isquarantined','Is quarantined'),
)

FILTER_BY = (
    (1,'is equal to'),
    (2,'is not equal to'),
    (3,'is greater than'),
    (4,'is less than'),
    (5,'contains'),
    (6,'does not contain'),
    (7,'matches regex'),
    (8,'does not match regex'),
    (9,'is null'),
    (10,'is not null'),
    (11,'is true'),
    (12,'is false'),
)

EMPTY_VALUES = (None, '')

BOOL_FIELDS = ["scaned", "spam", "highspam", "saspam", "rblspam",
    "whitelisted", "blacklisted", "virusinfected", "nameinfected",
    "otherinfected", "isquarantined"]
TEXT_FIELDS = ["id", "from_address", "from_domain", "to_address",
    "to_domain", "subject", "clientip", "spamreport", "headers"]
TIME_FIELDS = ["date","time"]
NUM_FIELDS = ["size", "sascore"]

BOOL_FILTER = [11, 12]
NUM_FILTER = [1, 2, 3, 4]
TEXT_FILTER = [1, 2, 5, 6, 7, 8, 9, 10]
TIME_FILTER = [1, 2, 3, 4]

def isnumeric(value):
    "Validate numeric values"
    return str(value).replace(".", "").replace("-", "").isdigit()

def to_dict(tuple_list):
    "Convert tuple to dictionary"
    dic = {}
    for val in tuple_list:
        dic[val[0]] = val[1]
    return dic

class FilterForm(forms.Form):
    "Filters form"
    filtered_field = forms.ChoiceField(choices=FILTER_ITEMS)
    filtered_by = forms.ChoiceField(choices=FILTER_BY)
    filtered_value = forms.CharField(required=False)

    def clean(self):
        "validate the form"
        cleaned_data = self.cleaned_data
        submited_field = cleaned_data.get('filtered_field')
        submited_by = int(cleaned_data.get('filtered_by'))
        submited_value = cleaned_data.get('filtered_value')
        if submited_by != 0:
            sbi = (submited_by - 1)
        else:
            sbi = submited_by

        if submited_field in BOOL_FIELDS:
            if not submited_by in BOOL_FILTER:
                filter_items = to_dict(list(FILTER_ITEMS))
                error_msg = "%s does not support the %s filter" % (
                    filter_items[submited_field],FILTER_BY[sbi][1])
                raise forms.ValidationError(error_msg)
        if submited_field in NUM_FIELDS:
            if not submited_by in NUM_FILTER:
                filter_items = to_dict(list(FILTER_ITEMS))
                error_msg = "%s does not support the %s filter" % (
                    filter_items[submited_field],FILTER_BY[sbi][1])
                raise forms.ValidationError(error_msg)
            if submited_value in EMPTY_VALUES:
                raise forms.ValidationError("Please supply a value to query")
            if not isnumeric(submited_value):
                raise forms.ValidationError("The value has to be numeric")
        if submited_field in TEXT_FIELDS:
            if not submited_by in TEXT_FILTER:
                filter_items = to_dict(list(FILTER_ITEMS))
                error_msg = "%s does not support the %s filter" % (
                    filter_items[submited_field],FILTER_BY[sbi][1])
                raise forms.ValidationError(error_msg)
            if submited_value in EMPTY_VALUES:
                raise forms.ValidationError("Please supply a value to query")
            if (submited_field == 'from_address') or (
                submited_field == 'to_address'):
                if not email_re.match(submited_value.strip()):
                    raise forms.ValidationError(
                        '%s is not a valid e-mail address.'
                        % force_escape(submited_value))
            if (submited_field == 'from_domain') or (
                submited_field == 'to_domain'):
                if not DOM_RE.match(submited_value.strip()):
                    raise forms.ValidationError(
                        'Please provide a valid domain name')
            if submited_field == 'clientip':
                if not ipv4_re.match(submited_value.strip()):
                    raise forms.ValidationError(
                        'Please provide a valid ipv4 address')
        if submited_field in TIME_FIELDS:
            if not submited_by in TIME_FILTER:
                filter_items = to_dict(list(FILTER_ITEMS))
                error_msg = "%s does not support the %s filter" % (
                    filter_items[submited_field],FILTER_BY[sbi][1])
                raise forms.ValidationError(error_msg)
            if submited_value in EMPTY_VALUES:
                raise forms.ValidationError("Please supply a value to query")
            if submited_field == 'date':
                try:
                    datetime.date(
                        *time.strptime(submited_value, '%Y-%m-%d')[:3])
                except ValueError:
                    raise forms.ValidationError(
                        'Please provide a valid date in YYYY-MM-DD format')
            if submited_field == 'time':
                try:
                    datetime.time(*time.strptime(submited_value, '%H:%M')[3:6])
                except ValueError:
                    raise forms.ValidationError(
                        'Please provide valid time in HH:MM format')

        return cleaned_data
