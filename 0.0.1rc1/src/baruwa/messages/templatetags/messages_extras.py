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
import os,re,GeoIP,socket
from textwrap import wrap
from django import template
from django.template.defaultfilters import stringfilter,wordwrap,linebreaksbr
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from baruwa.messages.models import SaRules
from baruwa.messages.process_mail import get_config_option,clean_regex

register = template.Library()

@register.filter(name='tds_msg_class')
def tds_msg_class(message):
    value = 'LightBlue'
    if message['isspam'] and not message['ishighspam'] and not message['spamblacklisted'] and not message['nameinfected'] and not message['otherinfected'] and not message['virusinfected']:
        value='spam'
    if message['ishighspam'] and (not message['spamblacklisted']):
        value='highspam'
    if message['spamwhitelisted']:
        value='whitelisted'
    if message['spamblacklisted']:
        value='blacklisted'
    if message['nameinfected'] or message['virusinfected']:
        value='infected'
    return mark_safe(value)

@register.filter(name='tds_msg_status')
def tds_msg_status(message):
    if message['isspam'] and (not message['spamblacklisted']) and (not message['virusinfected']) and (not message['nameinfected']) and (not message['otherinfected']):
        value = 'Spam'
    if message['spamblacklisted']:
        value = 'BL'
    if message['virusinfected'] or message['nameinfected'] or message['otherinfected']:
        value = 'Infected'
    if (not message['isspam']) and (not message['virusinfected']) and (not message['nameinfected']) and (not message['otherinfected']) and (not message['spamwhitelisted']):
        value = 'Clean'
    if message['spamwhitelisted']:
        value = 'WL'
    return value

@register.filter(name='tds_nl_commas')
@stringfilter
def tds_nl_commas(value):
    return value.replace(',', '\n')

@register.filter(name='tds_first')
@stringfilter
def tds_first(value):
    return value.split(',')[0]

@register.filter(name='tds_trunc')
@stringfilter
def tds_trunc(value,arg):
    value = value.strip()
    l = len(value)
    arg = int(arg)
    if l <= arg:
        return value
    else:
        if re.search(r'(\s)',value):
            tmp = wordwrap(value,arg)
            return linebreaksbr(tmp)
        else:
            suffix = '...'
            return value[0:arg] + suffix

@register.filter(name='tds_email_list')
@stringfilter
def tds_email_list(value):
    if re.match("default",value):
        value = "Any address"
    return value

@register.filter(name='tds_geoip')
@stringfilter
def tds_geoip(value):
    t = ""
    m = re.match(r'(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))',value)
    if m:
        gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
        try:
            cc = gip.country_code_by_addr(value).lower()
            cn = gip.country_name_by_addr(value)
        except:
            cc = None
            cn = None
        if cc and cn:
            t = '<img src="/static/imgs/flags/%s.png" alt="%s"/>' % (cc,cn)
    return mark_safe(t)

@register.filter(name='tds_hostname')
@stringfilter
def tds_hostname(value):
    hostname = ''
    m = re.match(r'(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))',value)
    if m:
        if m.groups()[0] == '127.0.0.1':
            hostname = 'localhost'
        else:
            try:
                hostname = socket.gethostbyaddr(m.groups()[0])[0]
            except:
                hostname = 'unknown'
    return mark_safe(hostname)

@register.filter(name='tds_is_learned')
@stringfilter
def tds_is_learned(value,autoescape=None):
    m = re.search(r'autolearn=((\w+\s\w+)|(\w+))',value)
    if m:
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        r = '<span class="positive">Y</span>&nbsp;(%s)' % (esc(m.group(1)))
    else:
        r = '<span class="negative">N</span>'
    return mark_safe(r)
tds_is_learned.needs_autoescape = True

@register.filter(name='tds_rbl_name')
@stringfilter
def tds_rbl_name(value,autoescape=None):
    r = ''
    m = re.search(r'^spam\,\s((?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\.?)',value)
    if m:
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        r = esc(m.group(1))
    return mark_safe(r)
tds_rbl_name.needs_autoescape = True

def tds_get_rules(rules):
    if not rules:
        return {}

    return_value = []
    sa_rule_descp = ""

    for rule in rules:
      rule = rule.strip()
      u = re.match(r'((\w+)(\s)(\d{1,2}\.\d{1,2}))',rule)
      if u:
        rule = u.groups()[1]
        try:
          d = SaRules.objects.get(rule__exact=rule)
          sa_rule_descp = d.rule_desc
        except:
          pass
        tdict = {'rule':rule,'score':u.groups()[3],'rule_descp':sa_rule_descp}
        return_value.append(tdict)
        sa_rule_descp = ""
    return return_value

@register.inclusion_tag('tags/spamreport.html')
def spam_report(value):
    if not value:
        return ""

    m = re.search(r'\((.+?)\)',value)
    if m:
        rules = m.groups()[0].split(',')
        return_value = tds_get_rules(rules)
    else:
        return_value = []
    return {'rules':return_value}

@register.filter(name='tds_wrap')
@stringfilter
def tds_wrap(value,length=100):
    length = int(length)
    if len(value) > length:
        value = '\n'.join(wrap(value,length))
    return value

@register.filter(name='tds_wrap_headers')
@stringfilter
def tds_wrap_headers(value):
    headers = value.split('\n')
    rstring = []
    for header in headers:
        if len(header) > 100:
            header = tds_wrap(header,100) #'\n'.join(wrap(header,100))
        rstring.append(header)
    return ('\n'.join(rstring))

def read_rules(filename):
    contents = []
    if os.path.exists(filename):
        f = open(filename)
        for line in f:
            if '#' in line:
                line, comment = line.split('#',1)
            contents.append(line)
        f.close()
    return contents

@register.simple_tag
def tds_action(value,from_address,to_address):
    rv = ''
    srules = []
    if value == 1:
        option = 'Spam Actions'
    else:
        option = 'High Scoring Spam Actions'
    rv = get_config_option(option)
    if re.match(r'^/.*[^/]$',rv):
        rules = read_rules(rv)
        for r in rules:
            sec={}
            m=re.match(r'^(\S+)\s+(\S+)(\s+(.*))?$',r)
            if m:
                (direction,rule,throwaway,value) = m.groups()
                throwaway=None
                m2 = re.match(r'^and\s+(\S+)\s+(\S+)(\s+(.+))?$',value)
                if m2:
                    (direction2,rule2,throwaway,value2) = m2.groups()
                    throwaway=None
                    sec = {'direction':direction2,'rule':clean_regex(rule2),'action':value2}
                srules.append({'direction':direction,'rule':clean_regex(rule),'action':value,'secondary':sec})
        for item in srules:
            if item["secondary"]:
                to_regex = ''
                from_regex = ''
                if re.match(r'from\:|fromorto\:',item["direction"],re.IGNORECASE):
                    from_regex = item['rule']
                if re.match(r'from\:|fromorto\:',item["secondary"]["direction"],re.IGNORECASE):
                    from_regex = item['secondary']['rule']
                if re.match(r'to\:|fromorto\:',item["direction"],re.IGNORECASE):
                    to_regex = item['rule']
                if re.match(r'to\:|fromorto\:',item["secondary"]["direction"],re.IGNORECASE):
                    to_regex = item['secondary']['rule']
                if to_regex == '' or from_regex == '':
                    return 'blank regex ' + to_regex + ' manoamano '+from_regex
                if re.match(to_regex,to_address,re.IGNORECASE) and re.match(from_regex,from_address,re.IGNORECASE):
                    return item["secondary"]["action"]
            else:
                comb_regex = ''
                to_regex = ''
                if re.match(r'to\:',item["direction"],re.IGNORECASE):
                    to_regex = item['rule']
                    if re.match(to_regex,to_address,re.IGNORECASE):
                        return item['action']
                if re.match(r'from\:|fromorto\:',item["direction"],re.IGNORECASE):
                    comb_regex = item['rule']
                    if re.match(comb_regex,from_address,re.IGNORECASE) or re.match(comb_regex,to_address,re.IGNORECASE):
                        return item["action"]
        return 'I do not know how to read it'
    else:
        return rv
    return rv

