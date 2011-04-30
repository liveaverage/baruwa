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

"Read mailq"
import os


class Mailq(list):
    "Mailq"

    def __init__(self, mta, queue):
        "init"
        assert mta in ['exim', 'sendmail', 'postfix'], "MTA not supported"
        assert os.path.isdir(queue), "Queue directory is not valid"
        list.__init__([])
        self.mta = mta
        self.queue = queue
        path = "baruwa.utils.mail.mta.%s" % mta
        module = __import__(path, None, None, ['QueueParser'])
        self.module = module.QueueParser(self.queue)

    def process(self):
        "process the queue"
        self.extend(self.module.process())

    def delete(self, items):
        "delete items"
        return self.module.delete(items)
