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
from django import template

register = template.Library()

def sorter(context, field_name, field_text):
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

    return { 'field_name': field_name,
        'field_text': field_text,
        'order_by': context['order_by'],
        'direction': context['direction'],
        'quarantine': quarantine,
        'app': context['app'],
    }
register.inclusion_tag('tags/sorter.html', takes_context=True)(sorter)
