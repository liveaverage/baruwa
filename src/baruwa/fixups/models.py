#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2011  Andrew Colin Kissa <andrew@topdog.za.net>
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

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import class_prepared
from django.core.validators import MaxLengthValidator


from baruwa.fixups import max_username_length


def long_username(sender, *args, **kwargs):
    """Override the built in username field"""
    if (sender.__name__ == "User" and
        sender.__module__ == "django.contrib.auth.models"):
        sender._meta.get_field("username").max_length = max_username_length()
        sender._meta.get_field("username").help_text = _("Required, %s "
            "characters or fewer. Only letters, numbers, and @, ., +, -, "
            "or _ characters." % max_username_length())

class_prepared.connect(long_username)


def patch_username():
    username = User._meta.get_field("username")
    username.max_length = max_username_length()
    for v in username.validators:
        if isinstance(v, MaxLengthValidator):
            v.limit_value = max_username_length()

patch_username()

