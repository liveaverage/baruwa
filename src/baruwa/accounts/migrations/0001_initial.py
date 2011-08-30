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

from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from baruwa.fixups import max_username_length

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.alter_column('auth_user', 'username', models.CharField(max_length=max_username_length()))
        #db.alter_column('sa_rules', 'rule', models.CharField(max_length=100))


    def backwards(self, orm):
        db.alter_column('auth_user', 'username', models.CharField(max_length=30))
        #db.alter_column('sa_rules', 'rule', models.CharField(max_length=25))


    models = {}