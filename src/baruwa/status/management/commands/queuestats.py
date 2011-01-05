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

"Queue stats generator"
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from optparse import make_option

class Command(BaseCommand):
    "Read the items in the queue and populate DB"
    option_list = BaseCommand.option_list + (
        make_option('--mta', dest='mta', default='exim', help='MTA'),
    )
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError(_("Command doesn't accept any arguments"))
        
        mtas = ['exim', 'sendmail', 'postfix']
        mta = options.get('mta')
        if not mta in mtas:
            raise CommandError(_("Only the following %(mta)s "
                                "MTA's are supported", 
                                {mta: ' '.join(mtas)}))
        pass