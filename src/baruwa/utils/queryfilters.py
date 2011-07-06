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

from django.db.models import Q

from baruwa.reports.forms import FILTER_ITEMS, FILTER_BY


def place_positive_vars(key, largs, kwargs, lkwargs, value):
    "utility function"
    if key in kwargs:
        kwords = {str(key): value}
        largs.append(Q(**kwords))
        kwords = {str(key): str(kwargs[key])}
        largs.append(Q(**kwords))
        lkwargs.update(kwords)
        del kwargs[key]
    else:
        kwords = {str(key): value}
        if key in lkwargs:
            largs.append(Q(**kwords))
        else:
            kwargs.update(kwords)


def place_negative_vars(key, nargs, nkwargs, lnkwargs, value):
    "utility function"
    if key in nkwargs:
        kwords = {str(key): value}
        nargs.append(Q(**kwords))
        kwords = {str(key): str(nkwargs[key])}
        nargs.append(Q(**kwords))
        lnkwargs.update(kwords)
        del nkwargs[key]
    else:
        kwords = {str(key): value}
        if key in lnkwargs:
            nargs.append(Q(**kwords))
        else:
            nkwargs.update(kwords)


def raw_user_filter(user, addresses, account_type):
    "builds user filter"
    dsql = []
    esql = []
    sql = '1 != 1'

    if not user.is_superuser:
        if account_type == 2:
            if addresses:
                for domain in addresses:
                    dsql.append('to_domain="' + domain + '"')
                    dsql.append('from_domain="' + domain + '"')
                sql = ' OR '.join(dsql)
        if account_type == 3:
            if addresses:
                for email in addresses:
                    esql.append('to_address="' + email + '"')
                    esql.append('from_address="' + email + '"')
                esql.append('to_address="' + user.username + '"')
                sql = ' OR '.join(esql)
            else:
                sql = 'to_address="%s"' % user.username
        return '(' + sql + ')'


def get_active_filters(filter_list, active_filters):
    "generates a dictionary of active filters"
    if not active_filters is None:
        filter_items = dict(FILTER_ITEMS)
        filter_by = dict(FILTER_BY)

        for filter_item in filter_list:
            active_filters.append(dict(
            filter_field=filter_items[filter_item['field']],
            filter_by=filter_by[int(filter_item['filter'])],
            filter_value=filter_item['value']))


def gen_dynamic_query(model, filter_list, active_filters=None):
    "build a dynamic query"
    kwargs = {}
    lkwargs = {}
    nkwargs = {}
    lnkwargs = {}
    nargs = []
    largs = []

    filter_items = dict(FILTER_ITEMS)
    filter_by = dict(FILTER_BY)

    for filter_item in filter_list:
        value = str(filter_item['value'])
        if filter_item['filter'] == 1:
            tmp = "%s__exact" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, value)
        if filter_item['filter'] == 2:
            tmp = "%s__exact" % filter_item['field']
            place_negative_vars(tmp, nargs, nkwargs, lnkwargs, value)
        if filter_item['filter'] == 3:
            tmp = "%s__gt" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, value)
        if filter_item['filter'] == 4:
            tmp = "%s__lt" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, value)
        if filter_item['filter'] == 5:
            tmp = "%s__icontains" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, value)
        if filter_item['filter'] == 6:
            tmp = "%s__icontains" % filter_item['field']
            place_negative_vars(tmp, nargs, nkwargs, lnkwargs, value)
        if filter_item['filter'] == 7:
            tmp = "%s__regex" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, value)
        if filter_item['filter'] == 8:
            tmp = "%s__regex" % filter_item['field']
            place_negative_vars(tmp, nargs, nkwargs, lnkwargs, value)
        if filter_item['filter'] == 9:
            tmp = "%s__isnull" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, value)
        if filter_item['filter'] == 10:
            tmp = "%s__isnull" % filter_item['field']
            place_negative_vars(tmp, nargs, nkwargs, lnkwargs, value)
        if filter_item['filter'] == 11:
            tmp = "%s__gt" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, 0)
        if filter_item['filter'] == 12:
            tmp = "%s__exact" % filter_item['field']
            place_positive_vars(tmp, largs, kwargs, lkwargs, 0)
        if not active_filters is None:
            active_filters.append(
                {
                'filter_field': filter_items[filter_item['field']],
                'filter_by': filter_by[int(filter_item['filter'])],
                'filter_value': value}
                )
    if kwargs:
        model = model.filter(**kwargs)
    if nkwargs:
        model = model.exclude(**nkwargs)
    if nargs:
        query = Q()
        for sub_query in nargs:
            query = query | sub_query
        model = model.exclude(query)
    if largs:
        query = Q()
        for sub_query in largs:
            query = query | sub_query
        model = model.filter(query)
    return model


def apply_filter(model, request, active_filters):
    "apply filters to a model"
    if request.session.get('filter_by', False):
        filter_list = request.session.get('filter_by')
        model = gen_dynamic_query(model, filter_list, active_filters)
    return model


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
                    avals.append('%' + filter_item['value'] + '%')
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
                    avals.append('%' + filter_item['value'] + '%')
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
                sql = andsql + ' AND ( ' + orsql + ' ) AND ( ' + nsql + ' )'
            else:
                sql = andsql + ' AND ( ' + orsql + ' )'
        else:
            if nsql != '':
                sql = andsql + ' AND ( ' + nsql + ' )'
            else:
                sql = andsql
    else:
        if orsql != '':
            if nsql != '':
                sql = '( ' + orsql + ' ) AND ( ' + nsql + ' )'
            else:
                sql = '( ' + orsql + ' )'
        else:
            if nsql != '':
                sql = '( ' + nsql + ' )'
            else:
                sql = ' 1=1 '
    return (sql, avals)

