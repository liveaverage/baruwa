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

"Status models"
from django.db import models


class MailQueueItem(models.Model):
    "MailQ item"
    id = models.AutoField(primary_key=True)
    messageid = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    from_address = models.CharField(blank=True, db_index=True, max_length=255)
    to_address = models.CharField(db_index=True, max_length=255)
    subject = models.TextField(blank=True)
    hostname = models.TextField()
    size = models.IntegerField()
    attempts = models.IntegerField()
    lastattempt = models.DateTimeField()
    direction = models.IntegerField(default=1, db_index=True)
    reason = models.TextField(blank=True)
    flag = models.IntegerField(default=0)

    class Meta:
        db_table = u'mailq'
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
