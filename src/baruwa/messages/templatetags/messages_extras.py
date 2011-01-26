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

import os, re, GeoIP, socket
from textwrap import wrap
from django import template
from django.template.defaultfilters import stringfilter, wordwrap, linebreaksbr
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from baruwa.messages.models import SaRules
from baruwa.utils.process_mail import clean_regex
from baruwa.utils.misc import get_config_option
from baruwa.utils.regex import RBL_RE, SARULE_RE, IP_RE, LEARN_RE

register = template.Library()

@register.filter(name='tds_msg_class')
def tds_msg_class(message):
    "set class"
    value = 'LightBlue'
    if (message['spam'] and not message['highspam'] and 
        not message['blacklisted'] and not message['nameinfected'] and 
        not message['otherinfected'] and not message['virusinfected']):
        value = 'spam'
    if message['highspam'] and (not message['blacklisted']):
        value = 'highspam'
    if message['whitelisted']:
        value = 'whitelisted'
    if message['blacklisted']:
        value = 'blacklisted'
    if message['nameinfected'] or message['virusinfected'] or message['otherinfected']:
        value = 'infected'
    if not message['scaned']:
        value = 'LightGray'
    return mark_safe(value)

@register.filter(name='tds_msg_status')
def tds_msg_status(message):
    "message status"
    if (message['spam'] and (not message['blacklisted']) 
        and (not message['virusinfected']) 
        and (not message['nameinfected']) 
        and (not message['otherinfected'])):
        value = 'Spam'
    if message['blacklisted']:
        value = 'BL'
    if (message['virusinfected'] or 
        message['nameinfected'] or 
        message['otherinfected']):
        value = 'Infected'
    if ((not message['spam']) and (not message['virusinfected']) 
        and (not message['nameinfected']) 
        and (not message['otherinfected']) 
        and (not message['whitelisted'])):
        value = 'Clean'
    if message['whitelisted']:
        value = 'WL'
    if not message['scaned']:
        value = 'NS'
    return value

@register.filter(name='tds_nl_commas')
@stringfilter
def tds_nl_commas(value):
    "commas to newlines"
    return value.replace(',', '\n')

@register.filter(name='tds_first')
@stringfilter
def tds_first(value):
    "get the first"
    return value.split(',')[0]

@register.filter(name='tds_trunc')
@stringfilter
def tds_trunc(value, arg):
    "truncate value"
    value = value.strip()
    length = len(value)
    arg = int(arg)
    if length <= arg:
        return value
    else:
        if re.search(r'(\s)', value):
            tmp = wordwrap(value, arg)
            return linebreaksbr(tmp)
        else:
            suffix = '...'
            return value[0:arg] + suffix

@register.filter(name='tds_email_list')
@stringfilter
def tds_email_list(value):
    "list email"
    if re.match("default", value):
        value = _("Any address")
    return value

@register.filter(name='tds_geoip')
@stringfilter
def tds_geoip(value):
    "return country flag"
    tag = ""
    match = IP_RE.match(value)
    if match:
        gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
        try:
            ccode = gip.country_code_by_addr(value).lower()
            cname = gip.country_name_by_addr(value)
        except:
            ccode = None
            cname = None
        if ccode and cname:
            tag = '<img src="/static/imgs/flags/%s.png" alt="%s"/>' % (
            ccode, cname)
    return mark_safe(tag)

@register.filter(name='tds_hostname')
@stringfilter
def tds_hostname(value):
    "display hostname"
    hostname = ''
    match = IP_RE.match(value)
    if match:
        if match.groups()[0] == '127.0.0.1':
            hostname = 'localhost'
        else:
            try:
                hostname = socket.gethostbyaddr(match.groups()[0])[0]
            except:
                hostname = _('unknown')
    return mark_safe(hostname)

@register.filter(name='tds_is_learned')
@stringfilter
def tds_is_learned(value, autoescape=None):
    "indicate learning status"
    match = LEARN_RE.search(value)
    if match:
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        status = '<span class="positive">Y</span>&nbsp;(%s)' % (
            esc(match.group(1)))
    else:
        status = '<span class="negative">N</span>'
    return mark_safe(status)
tds_is_learned.needs_autoescape = True

@register.filter(name='tds_rbl_name')
@stringfilter
def tds_rbl_name(value, autoescape=None):
    "get the rbl name"
    rbl = ''
    match = RBL_RE.search(value)
    if match:
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        rbl = esc(match.group(1))
    return mark_safe(rbl)
tds_rbl_name.needs_autoescape = True

def tds_get_rules(rules):
    "get spamassassin rules"
    if not rules:
        return {}

    return_value = []
    sa_rule_descp = ""

    for rule in rules:
        rule = rule.strip()
        match = SARULE_RE.match(rule)
        if match:
            rule = match.groups()[1]
            try:
                rule_obj = SaRules.objects.values(
                    'rule_desc').get(rule__exact=rule)
                sa_rule_descp = rule_obj['rule_desc']
            except:
                pass 
            return_value.append({'rule':rule, 'score':match.groups()[3], 
                'rule_descp':sa_rule_descp})
            sa_rule_descp = ""
    return return_value

@register.inclusion_tag('tags/spamreport.html')
def spam_report(value):
    "print spam report"
    if not value:
        return ""

    match = re.search(r'\((.+?)\)', value)
    if match:
        rules = match.groups()[0].split(',')
        return_value = tds_get_rules(rules)
    else:
        return_value = []
    return {'rules':return_value}

@register.filter(name='tds_wrap')
@stringfilter
def tds_wrap(value, length=100):
    "wrap a value"
    length = int(length)
    if len(value) > length:
        value = '\n'.join(wrap(value, length))
    return value

@register.filter(name='tds_wrap_headers')
@stringfilter
def tds_wrap_headers(value):
    "wrap the headers"
    headers = value.split('\n')
    rstring = []
    for header in headers:
        if len(header) > 100:
            header = tds_wrap(header, 100) #'\n'.join(wrap(header,100))
        rstring.append(header)
    return ('\n'.join(rstring))

def read_rules(filename):
    "read in rules"
    contents = []
    if os.path.exists(filename):
        rule_file = open(filename)
        for line in rule_file:
            if '#' in line:
                line, comment = line.split('#', 1)
            contents.append(line)
        rule_file.close()
    return contents

@register.simple_tag
def tds_action(value, from_address, to_address):
    "get actions"
    return_value = ''
    srules = []
    if value == 1:
        option = _('Spam Actions')
    else:
        option = _('High Scoring Spam Actions')
    return_value = get_config_option(option)
    if re.match(
        r'^/.*[^/]$', return_value) or re.match(r'(^%[a-z-]+%)(.*)', 
        return_value):
        match = re.match(r'(^%[a-z-]+%)(.*)', return_value)
        if match:
            the_dir = get_config_option(match.groups()[0])
            return_value = the_dir + match.groups()[1]
        rules = read_rules(return_value)
        for rule in rules:
            sec = {}
            match = re.match(r'^(\S+)\s+(\S+)(\s+(.*))?$', rule)
            if match:
                (direction, rule, throwaway, value) = match.groups()
                throwaway = None
                match2 = re.match(r'^and\s+(\S+)\s+(\S+)(\s+(.+))?$', value)
                if match2:
                    (direction2, rule2, throwaway, value2) = match2.groups()
                    throwaway = None
                    sec = {'direction':direction2, 
                        'rule':clean_regex(rule2), 'action':value2}
                srules.append({'direction':direction, 
                    'rule':clean_regex(rule), 'action':value, 'secondary':sec})
        for item in srules:
            if item["secondary"]:
                to_regex = ''
                from_regex = ''
                if re.match(
                    r'from\:|fromorto\:', item["direction"], re.IGNORECASE):
                    from_regex = item['rule']
                if re.match(
                    r'from\:|fromorto\:', item["secondary"]["direction"], 
                    re.IGNORECASE):
                    from_regex = item['secondary']['rule']
                if re.match(
                    r'to\:|fromorto\:', item["direction"], re.IGNORECASE):
                    to_regex = item['rule']
                if re.match(
                    r'to\:|fromorto\:', item["secondary"]["direction"], 
                    re.IGNORECASE):
                    to_regex = item['secondary']['rule']
                if to_regex == '' or from_regex == '':
                    return 'blank regex ' + to_regex + ' manoamano '+from_regex
                if (re.match(to_regex, to_address, re.IGNORECASE) and 
                    re.match(from_regex, from_address, re.IGNORECASE)):
                    return item["secondary"]["action"]
            else:
                comb_regex = ''
                to_regex = ''
                if re.match(r'to\:', item["direction"], re.IGNORECASE):
                    to_regex = item['rule']
                    if re.match(to_regex, to_address, re.IGNORECASE):
                        return item['action']
                if re.match(r'from\:|fromorto\:', item["direction"], 
                    re.IGNORECASE):
                    comb_regex = item['rule']
                    if (re.match(comb_regex, from_address, re.IGNORECASE) or 
                        re.match(comb_regex, to_address, re.IGNORECASE)):
                        return item["action"]
        return _('I do not know how to read it')
    else:
        return return_value
    return return_value
