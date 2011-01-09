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

from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def lists_sorter(context, field_name, field_text):
    "sort by field"
    rlink = None
    link = ''
    direc = 'dsc'
    if context['app'] == 'lists':
        link = reverse('lists-full-sort', args=[context['list_kind'], 
            context['direction'], field_name])
        if field_name == context['order_by']:
            if context['direction'] == 'dsc':
                direc = 'asc'
            else:
                direc = 'dsc'
            rlink = reverse('lists-full-sort', args=[context['list_kind'], 
                direc, context['order_by']])
    return {'field_text': field_text, 'link': link, 
        'rlink': rlink, 'dir': direc}
register.inclusion_tag('tags/sorter.html', takes_context=True)(lists_sorter)