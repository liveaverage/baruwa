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

from django.conf import settings
from django.db import connection
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _


class Command(NoArgsCommand):
    "Archive messages and delete from messages table"
    help = _("Deletes records older than QUARANTINE_DAYS_TO_KEEP"
    " days from the messages table")

    def handle_noargs(self, **options):
        #import datetime
        #from baruwa.messages.models import Message
        #interval = datetime.timedelta(days=60)
        #last_date = datetime.datetime.now() - interval
        #Message.objects.filter(timestamp__lt=last_date).delete()
        days = getattr(settings, 'QUARANTINE_DAYS_TO_KEEP', 60)

        conn = connection.cursor()
        conn.execute(
            """DELETE FROM messages WHERE id in 
            (SELECT id FROM archive WHERE timestamp <
            DATE_SUB(CURDATE(), INTERVAL %s DAY))
            """ % str(days)
        )
        conn.execute(
            """INSERT LOW_PRIORITY INTO archive
            SELECT * FROM messages WHERE timestamp <
            DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """ % str(days)
            
        )
        conn.execute(
            """DELETE LOW_PRIORITY FROM messages
            WHERE timestamp < DATE_SUB(CURDATE(),
            INTERVAL %s DAY)
            """ % str(days)
        )
        conn.execute('OPTIMIZE TABLE messages')
        conn.execute('OPTIMIZE TABLE archive')
