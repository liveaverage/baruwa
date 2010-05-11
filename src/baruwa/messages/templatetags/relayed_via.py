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
from django import template
from IPy import IP
import re,socket,GeoIP

register = template.Library()

@register.inclusion_tag('tags/relayed_via.html')
def relayed_via(headers):
    header_list = headers.split("\n")
    return_value = []
    ipaddr = ""
    for header in header_list:
        m = re.match(r'(^Received:|X-Originating-IP:)',header)
        if m:
            #m = re.findall(r'(\w+|\s|\()\[(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))\]',header)
            m = re.findall(r'((?:[0-9]{1,3})\.(?:[0-9]{1,3})\.(?:[0-9]{1,3})\.(?:[0-9]{1,3}))',header)
            if m:
                m.reverse()
                for l in m:
                    try:
                        iptype = IP(l).iptype()
                    except:
                        # psuedo work around if IPy not installed
                        if l == '127.0.0.1':
                            iptype = 'LOOPBACK'
                        else:
                            iptype = 'unknown'
                    country_code = ""
                    country_name = ""
                    if not iptype == "LOOPBACK" and l != ipaddr and l != '127.0.0.1':
                        ipaddr = l
                        try:
                            hostname = socket.gethostbyaddr(ipaddr)[0]
                        except:
                            if iptype == "PRIVATE":
                                hostname = "RFC1918 Private address"
                            else:
                                hostname = "Reverse lookup failed"
                        if iptype != "PRIVATE":
                            gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
                            try:
                                country_code = gip.country_code_by_addr(ipaddr).lower()
                                country_name = gip.country_name_by_addr(ipaddr)
                            except:
                                pass
                        tmp = {'ip_address':ipaddr,'hostname':hostname,'country_code':country_code,'country_name':country_name}
                        return_value.append(tmp)
    return {'hosts':return_value}
