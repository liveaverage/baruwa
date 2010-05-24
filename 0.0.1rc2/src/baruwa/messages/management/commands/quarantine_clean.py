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
import re

regex = re.compile(r"^\d{8}$")

def should_be_pruned(dir,days_to_retain):
    """
    Returns true or false :
    if the directory is older than days_to_retain
        returns true
    else
        returns false
    """

    import datetime

    if (not days_to_retain) or (not regex.match(dir)):
        return False

    interval = datetime.timedelta(days=days_to_retain)
    last_date = datetime.date.today() - interval
    y = int(dir[0:4])
    m = int(dir[4:-2])
    d = int(dir[6:])
    dir_date = datetime.date(y, m, d)

    return dir_date < last_date

class Command(NoArgsCommand):
    help = "Deletes quarantined files older than QUARANTINE_DAYS_TO_KEEP"

    def handle_noargs(self, **options):
        import os,shutil
        from django.conf import settings
        from baruwa.messages.process_mail import get_config_option
        from baruwa.messages.models import Maillog

        days_to_retain = getattr(settings, 'QUARANTINE_DAYS_TO_KEEP', 0)
        quarantine_dir = get_config_option('QuarantineDir')

        if quarantine_dir.startswith('/etc') or quarantine_dir.startswith('/lib') or quarantine_dir.startswith('/home') or \
                quarantine_dir.startswith('/bin') or quarantine_dir.startswith('..'):
            return False

        if (not os.path.exists(quarantine_dir)) or (days_to_retain == 0):
            return False

        ignore_dirs = ['spam','mcp','nonspam']

        dirs = [f for f in os.listdir(quarantine_dir) if os.path.isdir(os.path.join(quarantine_dir, f)) and regex.match(f) and should_be_pruned(f,days_to_retain)]
        dirs.sort()
        for d in dirs:
            print "======== Processing directory "+os.path.join(quarantine_dir,d)+" ==========="
            ids = [f for f in os.listdir(os.path.join(quarantine_dir, d)) if f not in ignore_dirs]
            if os.path.exists(os.path.join(quarantine_dir, d, 'spam')):
                ids.extend([f for f in os.listdir(os.path.join(quarantine_dir, d, 'spam'))])
            if os.path.exists(os.path.join(quarantine_dir, d, 'mcp')):
                ids.extend([f for f in os.listdir(os.path.join(quarantine_dir, d, 'mcp'))])
            if os.path.exists(os.path.join(quarantine_dir, d, 'nonspam')):
                ids.extend([f for f in os.listdir(os.path.join(quarantine_dir, d, 'nonspam'))])
            print ids
            Maillog.objects.filter(pk__in=ids).update(quarantined=0)
            if os.path.isabs(os.path.join(quarantine_dir,d)) and (not os.path.islink(os.path.join(quarantine_dir,d))):
                print "======== Removing directory   "+os.path.join(quarantine_dir,d)+" ==========="
                try:
                    shutil.rmtree(os.path.join(quarantine_dir,d))
                except:
                    print "Failed to remove "+os.path.join(quarantine_dir,d)
            else:
                print "The directory "+os.path.join(quarantine_dir,d)+" is a symbolic link skipping"

