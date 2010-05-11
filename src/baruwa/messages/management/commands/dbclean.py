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

# Some portions Copyright (C) 2003  Steve Freegard (smf@f2s.com)
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Deletes records older than 60 days from the maillog table"

    def handle_noargs(self, **options):
        from django.db import connection
        #import datetime
        #from baruwa.messages.models import Maillog
        #interval = datetime.timedelta(days=60)
        #last_date = datetime.datetime.now() - interval
        #Maillog.objects.filter(timestamp__lt=last_date).delete()

        c = connection.cursor()
        c.execute('INSERT LOW_PRIORITY INTO archive SELECT * FROM maillog WHERE timestamp < DATE_SUB(CURDATE(), INTERVAL 60 DAY)')
        c.execute('DELETE LOW_PRIORITY FROM maillog WHERE timestamp < DATE_SUB(CURDATE(), INTERVAL 60 DAY)')
        c.execute('OPTIMIZE TABLE maillog')
        c.execute('OPTIMIZE TABLE archive')
