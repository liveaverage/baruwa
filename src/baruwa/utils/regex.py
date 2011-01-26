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

import re

DOM_RE = re.compile(
        r'^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', 
        re.IGNORECASE
    )

IPV4_RE = re.compile(
    r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$'
    )

USER_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|"
    r"^([\001-\010\013\014\016-\037!#-\[\]-\177]|"
    r"\\[\001-011\013\014\016-\177])*)$", re.IGNORECASE)

ADDRESS_RE = re.compile(
r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  
r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|'
r'\\[\001-011\013\014\016-\177])*")' 
r'@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$'
r'|^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', 
re.IGNORECASE)

HOST_OR_IPV4_RE = re.compile(
    r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$'
    r'|^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', 
    re.IGNORECASE
)

IPV4_NET_OR_RANGE_RE = re.compile(
    r'^[.:\da-f]+\s*-\s*[.:\da-f]+$|'
    r'^([.:\da-f]+)\s*\/\s*([.:\da-f]+)$'
)

RBL_RE = re.compile(r'^spam\,\s+(.+),\s+SpamAssassin \(')

SARULE_RE = re.compile(r'((\w+)(\s)(\-?\d{1,2}\.\d{1,2}))')

LEARN_RE = re.compile(r'autolearn=((\w+\s\w+)|(\w+))')

IP_RE = re.compile(r'(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))')

