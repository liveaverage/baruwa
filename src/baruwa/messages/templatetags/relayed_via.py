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
