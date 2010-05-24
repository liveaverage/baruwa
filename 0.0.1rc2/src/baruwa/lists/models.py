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
from django.db import models

class Blacklist(models.Model):
    id = models.IntegerField(primary_key=True)
    to_address = models.TextField(unique=True)
    to_domain = models.TextField(blank=True)
    from_address = models.TextField(unique=True)

    class Meta:
        db_table = u'blacklist'
        get_latest_by = "id"
        ordering = ['-id']

    def delete(self, *args, **kwargs):
        if self.from_address == '127.0.0.1' and self.to_address == 'default':
            return
        else:
            super(Blacklist, self).delete(*args, **kwargs)

    def can_access(self, request):
        if not request.user.is_superuser:
            user_type = request.session['user_filter']['user_type']
            addresses = request.session['user_filter']['filter_addresses']
            a = [address.filter for address in addresses]
            if user_type == 'D':
                dom = self.to_address
                if '@' in dom:
                    dom = dom.split('@')[1]
                if dom not in a:
                    return False
            if user_type == 'U':
                if request.user.username != self.to_address:
                    if self.to_address not in a:
                        return False
        return True

class Whitelist(models.Model):
    id = models.IntegerField(primary_key=True)
    to_address = models.TextField(unique=True)
    to_domain = models.TextField(blank=True)
    from_address = models.TextField(unique=True)

    class Meta:
        db_table = u'whitelist'
        get_latest_by = "id"
        ordering = ['-id']

    def delete(self, *args, **kwargs):
        if self.from_address == '127.0.0.1' and self.to_address == 'default':
            return
        else:
            super(Whitelist, self).delete(*args, **kwargs)

    def can_access(self, request):
        if not request.user.is_superuser:
            user_type = request.session['user_filter']['user_type']
            addresses = request.session['user_filter']['filter_addresses']
            a = [address.filter for address in addresses]
            if user_type == 'D':
                dom = self.to_address
                if '@' in dom:
                    dom = dom.split('@')[1]
                if dom not in a:
                    return False
            if user_type == 'U':
                if request.user.username != self.to_address:
                    if self.to_address not in a:
                        return False
        return True
