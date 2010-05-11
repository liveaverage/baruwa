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
from django.core.urlresolvers import reverse

register = template.Library()

def sorter(context, field_name, field_text):
    rlink = None
    dir = 'dsc'
    if context.has_key('quarantine'):
        if context['quarantine'] == "1" or context['quarantine'] == 1:
            quarantine = "quarantine"
        else:
            quarantine = "full"
    else:
        if context['app'] == 'messages':
            quarantine = "full"
        else:
            quarantine = None
    if context['app'] == 'messages':
        if quarantine == 'full':
            url = 'messages-full-list'
        else:
            url = 'quarantine-full-list'
        link = reverse(url, args=[dir, field_name])
    else:
        link = reverse('lists-full-sort', args=[context['list_kind'], dir, field_name])

    if field_name == context['order_by']:
        if context['direction'] == 'dsc':
            dir = 'asc'
        else:
            dir = 'dsc'
        if context['app'] == 'messages':
            rlink = reverse(url, args=[dir, context['order_by']])
        else:
            rlink = reverse('lists-full-sort', args=[context['list_kind'], dir, field_name])

    return { 
        'field_text': field_text,
        'link': link,
        'rlink': rlink,
        'dir': dir,
    }
register.inclusion_tag('tags/sorter.html', takes_context=True)(sorter)
