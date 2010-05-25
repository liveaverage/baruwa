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


TYPE_CHOICES = (
    ('A', 'Administrator'),
    ('D', 'Domain admin'),
    ('U', 'User'),
    ('R', 'User (regex)'),
    ('H', 'Host'),
)

ACTIVE_CHOICES = (
    ('Y', 'Active'),
    ('N', 'Inactive'),
)

class UserFilters(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=60)
    filter = models.TextField()
    verify_key = models.CharField(max_length=96, blank=True)
    active = models.CharField(max_length=1, choices=ACTIVE_CHOICES, default='N')

    class Meta:
        db_table = u'user_filters'

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=60, unique=True)
    password = models.CharField(max_length=32)
    fullname = models.CharField(max_length=50)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='U')
    quarantine_report = models.IntegerField(default=0)
    spamscore = models.IntegerField(default=0)
    highspamscore = models.IntegerField(default=0)
    noscan = models.IntegerField(default=0)
    quarantine_rcpt = models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = u'users'
        verbose_name_plural = 'Users'
