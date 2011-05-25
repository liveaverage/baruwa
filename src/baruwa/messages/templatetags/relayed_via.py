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

from django import template
from django.utils.translation import ugettext as _
from IPy import IP

from baruwa.utils.misc import geoip_lookup
from baruwa.utils.regex import RELAY_HOSTS_RE, RECIEVED_RE

register = template.Library()


@register.inclusion_tag('tags/relayed_via.html')
def relayed_via(headers):
    "display relayed via"
    header_list = headers.split("\n")
    return_value = []
    ipaddr = ""
    for header in header_list:
        match = RECIEVED_RE.match(header)
        if match:
            match = RELAY_HOSTS_RE.findall(header)
            if match:
                match.reverse()
                for address in match:
                    addr = address[0] or address[1] or address[2]
                    try:
                        iptype = IP(addr).iptype()
                    except ValueError:
                        if addr == '127.0.0.1':
                            iptype = 'LOOPBACK'
                        else:
                            iptype = 'unknown'
                    country_code = "unknown"
                    country_name = ""
                    if (not iptype == "LOOPBACK"
                        and addr != ipaddr
                        and addr != '127.0.0.1'):
                        ipaddr = addr
                        try:
                            socket.setdefaulttimeout(60)
                            hostname = socket.gethostbyaddr(ipaddr)[0]
                        except (socket.error, socket.gaierror, socket.timeout):
                            if iptype == "PRIVATE":
                                hostname = _("RFC1918 Private address")
                            else:
                                hostname = _("Reverse lookup failed")
                        if iptype != "PRIVATE":
                            country_name, country_code = geoip_lookup(ipaddr)
                        return_value.append(dict(ip_address=ipaddr,
                        hostname=hostname or '&nbsp;',
                        country_code=country_code or 'unknown',
                        country_name=country_name or ''))
    return dict(hosts=return_value)
