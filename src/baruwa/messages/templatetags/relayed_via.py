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

from django import template
from django.utils.translation import ugettext_lazy as _
from IPy import IP
import re, socket, GeoIP

register = template.Library()

@register.inclusion_tag('tags/relayed_via.html')
def relayed_via(headers):
    "display relayed via"
    header_list = headers.split("\n")
    return_value = []
    ipaddr = ""
    for header in header_list:
        match = re.match(r'(^Received:|X-Originating-IP:)', header)
        if match:
            match = re.findall(
            r'((?:[0-9]{1,3})\.(?:[0-9]{1,3})\.(?:[0-9]{1,3})\.(?:[0-9]{1,3}))', 
            header)
            if match:
                match.reverse()
                for addr in match:
                    try:
                        iptype = IP(addr).iptype()
                    except:
                        # psuedo work around if IPy not installed
                        if addr == '127.0.0.1':
                            iptype = 'LOOPBACK'
                        else:
                            iptype = 'unknown'
                    country_code = ""
                    country_name = ""
                    if (not iptype == "LOOPBACK" 
                        and addr != ipaddr 
                        and addr != '127.0.0.1'):
                        ipaddr = addr
                        try:
                            hostname = socket.gethostbyaddr(ipaddr)[0]
                        except:
                            if iptype == "PRIVATE":
                                hostname = _("RFC1918 Private address")
                            else:
                                hostname = _("Reverse lookup failed")
                        if iptype != "PRIVATE":
                            gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
                            try:
                                country_code = gip.country_code_by_addr(ipaddr).lower()
                                country_name = gip.country_name_by_addr(ipaddr)
                            except:
                                pass
                        return_value.append(
                            {'ip_address':ipaddr, 
                            'hostname':hostname, 
                            'country_code':country_code, 
                            'country_name':country_name})
    return {'hosts':return_value}
