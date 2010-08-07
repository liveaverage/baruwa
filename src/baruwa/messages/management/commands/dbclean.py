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

from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    "Archive messages and delete from messages table"
    help = "Deletes records older than 60 days from the messages table"

    def handle_noargs(self, **options):
        from django.db import connection
        #import datetime
        #from baruwa.messages.models import Message
        #interval = datetime.timedelta(days=60)
        #last_date = datetime.datetime.now() - interval
        #Message.objects.filter(timestamp__lt=last_date).delete()

        conn = connection.cursor()
        conn.execute(
            """INSERT LOW_PRIORITY INTO archive 
            SELECT * FROM messages WHERE timestamp < 
            DATE_SUB(CURDATE(), INTERVAL 60 DAY)"""
        )
        conn.execute(
            """DELETE LOW_PRIORITY FROM messages 
            WHERE timestamp < DATE_SUB(CURDATE(), 
            INTERVAL 60 DAY)"""
        )
        conn.execute('OPTIMIZE TABLE messages')
        conn.execute('OPTIMIZE TABLE archive')
