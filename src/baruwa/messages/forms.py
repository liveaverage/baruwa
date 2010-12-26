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


SALEARN_OPTIONS = (
  ('1', _('Spam')),
  ('2', _('Ham')),
  ('3', _('Forget')),
)

EMPTY_VALUES = (None, '')

class QuarantineProcessForm(forms.Form):
    """
    Generates a quarantine process form,
    it can be used to release, sa learn or
    delete a quarantined message
    """
    salearn = forms.BooleanField(required=False)
    salearn_as = forms.ChoiceField(choices=SALEARN_OPTIONS)
    release = forms.BooleanField(required=False)
    todelete = forms.BooleanField(required=False)
    use_alt = forms.BooleanField(required=False)
    altrecipients = forms.CharField(required=False)
    message_id = forms.CharField(widget=forms.HiddenInput)

    def clean(self):
        """
        Validates the quarantine form
        """
        cleaned_data = self.cleaned_data
        use_alt = cleaned_data.get("use_alt")
        altrecipients = cleaned_data.get("altrecipients")
        salearn = cleaned_data.get("salearn")
        release = cleaned_data.get("release")
        todelete = cleaned_data.get("todelete")

        if not salearn and not release and not todelete:
            raise forms.ValidationError(_("Select atleast one action to perform"))
        else:
            if altrecipients in EMPTY_VALUES and use_alt and release:
                raise forms.ValidationError(
                    _("Provide atleast one alternative recipient"))
            else:
                if use_alt and release:
                    emails = altrecipients.split(',')
                    for email in emails:
                        if not email_re.match(email.strip()):
                            raise forms.ValidationError(
                            _('%(email)s is not a valid e-mail address.') 
                            % {'email':force_escape(email)})
        return cleaned_data
