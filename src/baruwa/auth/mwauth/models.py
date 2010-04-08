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
from django.db import models

# Create your models here.
class UserFilters(models.Model):
    username = models.CharField(max_length=60)
    filter = models.TextField()
    verify_key = models.CharField(max_length=96)
    active = models.CharField(max_length=3)
    class Meta:
        db_table = u'user_filters'

class Users(models.Model):
    username = models.CharField(max_length=60, primary_key=True)
    password = models.CharField(max_length=32)
    fullname = models.CharField(max_length=50)
    type = models.CharField(max_length=3)
    quarantine_report = models.IntegerField(null=True, blank=True)
    spamscore = models.IntegerField(null=True, blank=True)
    highspamscore = models.IntegerField(null=True, blank=True)
    noscan = models.IntegerField(null=True, blank=True)
    quarantine_rcpt = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'users'
