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

class BaruwaDBRouter(object):
    """Route DB operations between the mail and web DB's"""

    def db_for_read(self, model, **hints):
        "Point all web operations to 'web'"
        if model._meta.app_label == 'web':
            return 'web'
        return None

    def db_for_write(self, model, **hints):
        "Point all web operations to 'web'"
        if model._meta.app_label == 'web':
            return 'web'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a models are web models"
        print obj1, obj2
        if obj1._meta.app_label == 'web' or obj2._meta.app_label == 'web':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the web models sync to web db"
        if db == 'web':
            return model._meta.app_label == 'web'
        elif model._meta.app_label == 'web':
            return False
        return None
