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

"HTTP class to make remote requests"
from django.conf import settings
if settings.SESSION_COOKIE_SECURE:
    from httplib import HTTPSConnection as HTTPConnection
else:
    from httplib import HTTPConnection


class ProcessRemote(HTTPConnection):
    "Inherit from httplib"

    headers = {'X-Requested-With': 'XMLHttpRequest'}

    def __init__(self, host, url, cookie=None, params=None):
        "init"
        self.url = url
        if not self.url.startswith('/'):
            self.url = '/' + self.url
        if not self.url.endswith('/'):
            self.url = self.url + '/'
        if cookie:
            self.headers['Cookie'] = cookie
        self.params = params
        HTTPConnection.__init__(self, host)

    def post(self):
        "POST"
        self.request('POST', self.url, self.params, self.headers)
        self.response = self.getresponse()
        self.close()

    def get(self):
        "GET"
        self.request('GET', self.url, self.params, self.headers)
        self.response = self.getresponse()
        self.close()
