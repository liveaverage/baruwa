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

from django.db import models
from baruwa.accounts.models import UserAddresses

class MailAuthHost(models.Model):
    "Holds authentication hosts"
    
    AUTH_TYPE = (
        (1, 'POP3'),
        (2, 'IMAP'),
        (3, 'SMTP'),
    )
    
    address = models.CharField(max_length=255)
    protocol = models.IntegerField(choices=AUTH_TYPE, default=1)
    port = models.IntegerField(blank=True)
    enabled = models.BooleanField(default=True)
    split_address = models.BooleanField()
    useraddress = models.ForeignKey(UserAddresses)
    
    class Meta:
        db_table = 'auth_hosts'
        