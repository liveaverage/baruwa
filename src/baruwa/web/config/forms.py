#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2012  Andrew Colin Kissa <andrew@topdog.za.net>
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

from baruwa.web.config.models import Time, Source, Destination, AclRule
from baruwa.web.config.models import DestinationComponent, DestinationPolicy
from baruwa.web.config.models import OrderedDestination


class TimeBase(forms.ModelForm):
    class Meta:
        model = Time


class TimeForm(forms.ModelForm):
    class Meta:
        exclude = ('id',)
        model = Time


class SourceForm(forms.ModelForm):
    class Meta:
        exclude = ('id',)
        model = Source


class DestForm(forms.ModelForm):
    class Meta:
        exclude = ('id',)
        model = Destination


class DCForm(forms.ModelForm):
    class Meta:
        exclude = ('id',)
        model = DestinationComponent


class ODSForm(forms.ModelForm):
    class Meta:
        exclude = ('id', 'order',)
        model = OrderedDestination


class DPSForm(forms.ModelForm):
    class Meta:
        exclude = ('id',)
        model = DestinationPolicy


class ACLForm(forms.ModelForm):
    class Meta:
        exclude = ('id', 'order',)
        model = AclRule


class ApplyForm(forms.Form):
    sentry = forms.CharField(widget=forms.HiddenInput)
    