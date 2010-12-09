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
from django.utils.translation import ugettext as _
import re

REGEX = re.compile(r"^\d{8}$")

def should_be_pruned(direc, days_to_retain):
    """
    Returns true or false :
    if the directory is older than days_to_retain
        returns true
    else
        returns false
    """

    import datetime

    if (not days_to_retain) or (not REGEX.match(direc)):
        return False

    interval = datetime.timedelta(days=days_to_retain)
    last_date = datetime.date.today() - interval
    year = int(direc[0:4])
    mon = int(direc[4:-2])
    day = int(direc[6:])
    dir_date = datetime.date(year, mon, day)

    return dir_date < last_date

class Command(NoArgsCommand):
    "cleans the quarantine directory"
    help = "Deletes quarantined files older than QUARANTINE_DAYS_TO_KEEP"

    def handle_noargs(self, **options):
        import os, shutil
        from django.conf import settings
        from baruwa.utils.misc import get_config_option
        from baruwa.messages.models import Message

        days_to_retain = getattr(settings, 'QUARANTINE_DAYS_TO_KEEP', 0)
        quarantine_dir = get_config_option('QuarantineDir')

        if (quarantine_dir.startswith('/etc') or
            quarantine_dir.startswith('/lib') or
            quarantine_dir.startswith('/home') or
            quarantine_dir.startswith('/bin') or
            quarantine_dir.startswith('..')):
            return False

        if (not os.path.exists(quarantine_dir)) or (days_to_retain == 0):
            return False

        ignore_dirs = ['spam', 'mcp', 'nonspam']

        dirs = [
        f for f in os.listdir(quarantine_dir)
        if os.path.isdir(
            os.path.join(quarantine_dir, f)
            ) and REGEX.match(f) and should_be_pruned(f, days_to_retain)
        ]
        dirs.sort()
        for direc in dirs:
            process_path = os.path.join(quarantine_dir, direc)
            print _("== Processing directory %(path)s ==") % {'path':process_path}
            ids = [f for f in os.listdir(process_path) if f not in ignore_dirs]
            
            if os.path.exists(os.path.join(process_path, 'spam')):
                ids.extend(
                [f for f in os.listdir(os.path.join(process_path, 'spam'))])
                
            if os.path.exists(os.path.join(process_path, 'mcp')):
                ids.extend(
                [f for f in os.listdir(os.path.join(process_path, 'mcp'))])
                
            if os.path.exists(os.path.join(process_path, 'nonspam')):
                ids.extend(
                [f for f in os.listdir(os.path.join(process_path, 'nonspam'))])
                
            print ids
            Message.objects.filter(pk__in=ids).update(isquarantined=0)
            if (os.path.isabs(process_path) and 
                (not os.path.islink(process_path))):
                print _("== Removing directory  %(path)s ==") % {'path':process_path}
                try:
                    shutil.rmtree(process_path)
                except:
                    print _("Failed to remove %(path)s") % {'path':process_path}
            else:
                print _("The directory %(path)s is a sym link skipping") % {'path':process_path}
