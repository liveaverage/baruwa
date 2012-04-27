#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2012  Andrew Colin Kissa <andrew@topdog.za.net>
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

from django.db.models import Count, Sum
from django.utils.translation import ugettext as _

from baruwa.utils.graphs import PIE_COLORS
from baruwa.utils.queryfilters import apply_filter
from baruwa.web.visits.models import Traffic, Virusdetection, SearchqueryInfo


REPORT_DICT = {
    1: {'queryfield': 'site__category', 'exclude': {'site__category__exact': ''}, 'order': '-num_count', 'model': Traffic, 'size': 'bytes', 'title': _('Top Categories by Quantity')},
    2: {'queryfield': 'site__category', 'exclude': {'site__category__exact': ''}, 'order': '-total_size', 'model': Traffic, 'size': 'bytes', 'title': _('Top Categories by Volume')},
    3: {'queryfield': 'site__site', 'exclude': {'site__site__exact': ''}, 'order': '-num_count', 'model': Traffic, 'size': 'bytes', 'title': _('Top Sites by Quantity')},
    4: {'queryfield': 'site__site', 'exclude': {'site__site__exact': ''}, 'order': '-total_size', 'model': Traffic, 'size': 'bytes', 'title': _('Top Sites by Volume')},
    5: {'queryfield': 'virusname', 'exclude': {'virusname__exact': ''}, 'order': '-num_count', 'model': Virusdetection, 'size': 'traffic__bytes', 'title': _('Top Detected Viruses by Quantity')},
    6: {'queryfield': 'virusname', 'exclude': {'virusname__exact': ''}, 'order': '-total_size', 'model': Virusdetection, 'size': 'traffic__bytes', 'title': _('Top Detected Viruses by Volume')},
    7: {'queryfield': 'bytes', 'exclude': {'bytes__exact': '0'}, 'order': '-num_count', 'model': Traffic, 'size': 'bytes', 'title': _('Top Files by Quantity')},
    8: {'queryfield': 'bytes', 'exclude': {'bytes__exact': '0'}, 'order': '-total_size', 'model': Traffic, 'size': 'bytes', 'title': _('Top Files by Volume')},
    9: {'queryfield': 'ip__hostname', 'exclude': {'ip__hostname__exact': '0'}, 'order': '-num_count', 'model': Traffic, 'size': 'bytes', 'title': _('Top Hosts by Quantity')},
    10: {'queryfield': 'ip__hostname', 'exclude': {'ip__hostname__exact': '0'}, 'order': '-total_size', 'model': Traffic, 'size': 'bytes', 'title': _('Top Hosts by Volume')},
    11: {'queryfield': 'user__authuser', 'exclude': {'user__authuser__exact': ''}, 'order': '-num_count', 'model': Traffic, 'size': 'bytes', 'title': _('Top Users By Quantity')},
    12: {'queryfield': 'user__authuser', 'exclude': {'user__authuser__exact': ''}, 'order': '-total_size', 'model': Traffic, 'size': 'bytes', 'title': _('Top Users By Volume')},
    13: {'queryfield': 'query', 'exclude': {'query__exact': ''}, 'order': '-num_count', 'model': SearchqueryInfo, 'size': 'traffic__bytes', 'title': _('Top Search Phrases By Quantity')},
    14: {'queryfield': 'query', 'exclude': {'query__exact': ''}, 'order': '-total_size', 'model': SearchqueryInfo, 'size': 'traffic__bytes', 'title': _('Top Search Phrases By Volume')},
}


def run_query(reportid, request, active_filters):
    "run a query"
    query_field = REPORT_DICT[reportid]['queryfield']
    exclude_kwargs = REPORT_DICT[reportid]['exclude']
    order_by = REPORT_DICT[reportid]['order']
    size_field = REPORT_DICT[reportid]['size']
    model = REPORT_DICT[reportid]['model']
    data = model.objects.values(query_field)\
            .exclude(**exclude_kwargs)\
            .annotate(num_count=Count(query_field), total_size=Sum(size_field))\
            .order_by(order_by)
    data = apply_filter(data, request, active_filters, True)
    data = data[:10]
    return data


def pack_json_data(data, reportid):
    "creates the json for the svn pie charts"
    arg1 = REPORT_DICT[reportid]['queryfield']
    arg2 = REPORT_DICT[reportid]['order'].lstrip('-')
    ret = []

    for index, item in enumerate(data):
        pie_data = {}
        pie_data['y'] = item[arg2]
        pie_data['color'] = PIE_COLORS[index]
        pie_data['stroke'] = 'black'
        pie_data['tooltip'] = str(item[arg1])
        ret.append(pie_data)
    return ret