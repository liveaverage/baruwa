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

from django.db.models import Count, Sum, Q

from baruwa.utils.queryfilters import apply_filter
from baruwa.messages.models import Message
from baruwa.utils.graphs import PIE_COLORS


def pack_json_data(data, arg1, arg2):
    "creates the json for the svn pie charts"
    ret = []

    for index, item in enumerate(data):
        pie_data = {}
        pie_data['y'] = item[arg2]
        pie_data['color'] = PIE_COLORS[index]
        pie_data['stroke'] = 'black'
        pie_data['tooltip'] = item[arg1]
        ret.append(pie_data)
    return ret


def run_hosts_query(request, active_filters):
    "run the top hosts query"
    data = Message.messages.for_user(request).values('clientip').exclude(
        Q(clientip__exact='') | Q(clientip__exact='127.0.0.1') |
        Q(clientip__isnull=True)).annotate(num_count=Count('clientip'),
        total_size=Sum('size'), virus_total=Sum('virusinfected'),
        spam_total=Sum('spam')).order_by('-num_count')
    data = apply_filter(data, request, active_filters)
    data = data[:10]
    return data


def run_query(query_field, exclude_kwargs, order_by, request, active_filters):
    "run a query"
    data = Message.messages.for_user(request).values(query_field).exclude(
    **exclude_kwargs).annotate(num_count=Count(query_field),
    total_size=Sum('size')).order_by(order_by)
    data = apply_filter(data, request, active_filters)
    data = data[:10]
    return data
