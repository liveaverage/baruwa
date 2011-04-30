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

"Config tasks"

from celery.task import Task
from django.utils.translation import ugettext as _
from baruwa.utils.mail.message import TestDeliveryServers


class TestSMTPServer(Task):
    "Tests a delivery server"
    name = 'test-smtp-server'
    serializer = 'json'

    def run(self, host, port, from_addr,
        to_addr, host_id, count=None, **kwargs):
        "run"
        result = {'errors': {}, 'host': host_id}
        logger = self.get_logger(**kwargs)
        logger.info(_("Starting connection tests to: %(host)s") % {
        'host': host})
        server = TestDeliveryServers(host, port, to_addr, from_addr)
        if server.ping(count):
            result['ping'] = True
        else:
            result['ping'] = False
            result['errors']['ping'] = ' '.join(server.errors)
            server.reset_errors()
        if server.smtp_test():
            result['smtp'] = True
        else:
            result['smtp'] = False
            result['errors']['smtp'] = ' '.join(server.errors)
        return result
