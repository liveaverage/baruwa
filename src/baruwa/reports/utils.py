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

from django.db.models import Count, Sum, Q
from baruwa.messages.models import Message
from baruwa.utils.misc import apply_filter
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
        Q(clientip__exact = '') | Q(clientip__exact = '127.0.0.1') |
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


def gen_dynamic_raw_query(filter_list):
    "generates a dynamic query"
    sql = []
    asql = []
    avals = []
    osql = []
    ovals = []
    nosql = []
    novals = [] 

    for filter_item in filter_list:
        if filter_item['filter'] == 1:
            tmp = "%s = %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                osql.append(asql[inx])
                ovals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                osql.append(tmp)
                ovals.append(filter_item['value'])
            else:
                if tmp in osql:
                    osql.append(tmp)
                    ovals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append(filter_item['value'])
        if filter_item['filter'] == 2:
            tmp = "%s != %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                nosql.append(asql[inx])
                novals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                nosql.append(tmp)
                novals.append(filter_item['value'])
            else:
                if tmp in nosql:
                    nosql.append(tmp)
                    novals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append(filter_item['value'])
        if filter_item['filter'] == 3:
            tmp = "%s > %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                osql.append(asql[inx])
                ovals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                osql.append(tmp)
                ovals.append(filter_item['value'])
            else:
                if tmp in osql:
                    osql.append(tmp)
                    ovals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append(filter_item['value'])
        if filter_item['filter'] == 4:
            tmp = "%s < %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                osql.append(asql[inx])
                ovals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                osql.append(tmp)
                ovals.append(filter_item['value'])
            else:
                if tmp in osql:
                    osql.append(tmp)
                    ovals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append(filter_item['value'])
        if filter_item['filter'] == 5:
            tmp = "%s LIKE %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                osql.append(asql[inx])
                ovals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                osql.append(tmp)
                ovals.append(filter_item['value'])
            else:
                if tmp in osql:
                    osql.append(tmp)
                    ovals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append('%'+filter_item['value']+'%')
        if filter_item['filter'] == 6:
            tmp = "%s NOT LIKE %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                nosql.append(asql[inx])
                novals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                nosql.append(tmp)
                novals.append(filter_item['value'])
            else:
                if tmp in nosql:
                    nosql.append(tmp)
                    novals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append('%'+filter_item['value']+'%')
        if filter_item['filter'] == 7:
            tmp = "%s REGEXP %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                osql.append(asql[inx])
                ovals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                osql.append(tmp)
                ovals.append(filter_item['value'])
            else:
                if tmp in osql:
                    osql.append(tmp)
                    ovals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append(filter_item['value'])
        if filter_item['filter'] == 8:
            tmp = "%s NOT REGEXP %%s" % filter_item['field']
            if tmp in asql:
                inx = asql.index(tmp)
                tvl = avals[inx]

                nosql.append(asql[inx])
                novals.append(tvl)

                asql.remove(tmp)
                avals.remove(tvl)

                nosql.append(tmp)
                novals.append(filter_item['value'])
            else:
                if tmp in nosql:
                    nosql.append(tmp)
                    novals.append(filter_item['value'])
                else:
                    asql.append(tmp)
                    avals.append(filter_item['value'])
        if filter_item['filter'] == 9:
            tmp = "%s IS NULL" % filter_item['field']
            sql.append(tmp)
        if filter_item['filter'] == 10:
            tmp = "%s IS NOT NULL" % filter_item['field']
            sql.append(tmp)
        if filter_item['filter'] == 11:
            tmp = "%s > 0" % filter_item['field']
            sql.append(tmp)
        if filter_item['filter'] == 12:
            tmp = "%s = 0" % filter_item['field']
            sql.append(tmp)
    for item in sql:
        asql.append(item)

    andsql = ' AND '.join(asql)
    orsql = ' OR '.join(osql)
    nsql = ' AND '.join(nosql)

    for item in ovals:
        avals.append(item)

    for item in novals:
        avals.append(item)

    if andsql != '':
        if orsql != '':
            if nsql != '':
                sql = andsql + ' AND ( '+orsql+' ) AND ( '+nsql+' )'
            else:
                sql = andsql + ' AND ( '+orsql+' )'
        else:
            if nsql != '':
                sql = andsql + ' AND ( '+nsql+' )'
            else:
                sql = andsql
    else:
        if orsql != '':
            if nsql != '':
                sql = '( '+orsql+' ) AND ( '+nsql+' )'
            else:
                sql = '( '+orsql+' )'
        else:
            if nsql != '':
                sql = '( '+nsql+' )'
            else:
                sql = ' 1=1 '
    return (sql, avals)
