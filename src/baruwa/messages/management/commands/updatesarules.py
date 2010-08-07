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
    "update the rules table"
    help = "Updates the database with the spam descriptions"

    def handle_noargs(self, **options):
        import re, glob, os
        from django.conf import settings
        from baruwa.messages.models import SaRules

        search_dirs = getattr(settings, 'SA_RULES_DIRS', [])
        regex = re.compile(r'^describe\s+(\S+)\s+(.+)$')
        for dirc in search_dirs:
            if not dirc.endswith(os.sep):
                dirc = dirc + os.sep
            for the_file in glob.glob(dirc + '*.cf'):
                rule_file = open(the_file, 'r')
                for line in rule_file.readlines():
                    match = regex.match(line)
                    if match:
                        print match.groups()[0] + ' ' + match.groups()[1]
                        rule = SaRules(rule = match.groups()[0], 
                        rule_desc = match.groups()[1])
                        try:
                            rule.save()
                        except:
                            pass
                rule_file.close()
