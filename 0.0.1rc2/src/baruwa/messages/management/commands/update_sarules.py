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
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Updates the database with the spam descriptions"

    def handle_noargs(self, **options):
        import re, glob, os
        from django.conf import settings
        from baruwa.reports.models import SaRules

        search_dirs = getattr(settings, 'SA_RULES_DIRS',[])
        regex = re.compile(r'^describe\s+(\S+)\s+(.+)$')
        for dir in search_dirs:
            if not dir.endswith(os.sep):
                dir = dir + os.sep
            for file in glob.glob(dir + '*.cf'):
                f = open(file,'r')
                for line in f.readlines():
                    m = regex.match(line)
                    if m:
                        print m.groups()[0] + ' ' + m.groups()[1]
                        rule = SaRules(rule=m.groups()[0],rule_desc=m.groups()[1])
                        rule.save()
                f.close()
