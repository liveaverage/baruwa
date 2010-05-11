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

class SavedFilters(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    col = models.TextField(unique=True)
    operator = models.TextField(unique=True)
    value = models.TextField(unique=True)
    username = models.TextField(unique=True)

    class Meta:
        db_table = u'saved_filters'

class SaRules(models.Model):
    rule = models.CharField(max_length=100, primary_key=True)
    rule_desc = models.CharField(max_length=200)

    class Meta:
        db_table = u'sa_rules'

