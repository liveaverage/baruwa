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
from django.contrib.auth.models import User

class List(models.Model):
    """
    Spam Whitelist and Blacklist
    """
    id = models.AutoField(primary_key=True)
    list_type = models.IntegerField(default=0)
    from_address = models.CharField(default='any', max_length=255)
    to_address = models.CharField(default='any', max_length=255)
    user = models.ForeignKey(User)
    
    class Meta:
        db_table = 'lists'
        #mysql utf8 bug prevents this being used.
        #unique_together = ('from_address', 'to_address')

    def can_access(self, request):
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            addresses = request.session['user_filter']['addresses']
            if account_type == 2:
                dom = self.to_address
                if '@' in dom:
                    dom = dom.split('@')[1]
                if dom not in addresses:
                    return False
            if account_type == 3:
                if request.user.username != self.to_address:
                    if self.to_address not in addresses:
                        return False
        return True
