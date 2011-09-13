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

import socket

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from django.db import DatabaseError

from baruwa.utils.misc import host_is_local
from baruwa.config.models import ScannerHost

class Command(NoArgsCommand):
    "cleans the quarantine directory"
    help = "Sets up system to handle SQL configuration"

    def handle_noargs(self, **options):
        "handle"
        hostname = socket.gethostname() or ''
        prompt = _("Please enter the hostname [%s]: ") % hostname
        while 1:
            try:
                value = raw_input(prompt)
                if not value:
                    value = hostname
                value = value.strip()
                if not host_is_local(value):
                    print _("The hostname %(h)s is not assigned"
                            " to this system, try again") % dict(h=value)
                    continue
                host = ScannerHost.objects.filter(address=value)
                if not host:
                    host = ScannerHost(address=value)
                    try:
                        host.save()
                        print _("The host: %(h)s has been initialized")\
                                % dict(h=value)
                    except DatabaseError:
                        print _("The settings could not be saved"
                                " check your DB settings")
                    break
                else:
                    print _("The host: %(h)s is already initialized")\
                            % dict(h=value)
                    break
            except (KeyboardInterrupt, EOFError):
                break
