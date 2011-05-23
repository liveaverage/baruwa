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

import socket
import GeoIP
import subprocess

from IPy import IP
from django.conf import settings
from django.db.models import Q, Count
from django.template.defaultfilters import force_escape


def jsonify_msg_list(element):
    """
    Fixes the converting error in converting
    DATETIME objects to JSON
    """
    element['timestamp'] = str(element['timestamp'])
    element['sascore'] = str(element['sascore'])
    element['subject'] = force_escape(element['subject'])
    element['to_address'] = force_escape(element['to_address'])
    element['from_address'] = force_escape(element['from_address'])
    return element


def jsonify_list(element):
    """jsonify_list"""
    element['id'] = str(element['id'])
    element['from_address'] = force_escape(element['from_address'])
    element['to_address'] = force_escape(element['to_address'])
    return element


def jsonify_accounts_list(element):
    "Jsonify accounts list"
    element['id'] = str(element['id'])
    return element


def jsonify_domains_list(element):
    "Jsonify domains list"
    element['id'] = str(element['id'])
    element['user__id'] = str(element['user__id'])
    return element


def jsonify_status(element):
    "Jsonify status dict"
    for key in ['baruwa_spam_total', 'baruwa_virus_total',
    'baruwa_mail_total']:
        element[key] = str(element[key])
    return element


def apply_filter(model, request, active_filters):
    "apply filters to a model"
    if request.session.get('filter_by', False):
        filter_list = request.session.get('filter_by')
        model = gen_dynamic_query(model, filter_list, active_filters)
    return model


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


def gen_dynamic_query(model, filter_list, active_filters=None):
    "build a dynamic query"
    from baruwa.reports.forms import FILTER_ITEMS, FILTER_BY
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
    from baruwa.reports.forms import FILTER_ITEMS, FILTER_BY
    if not active_filters is None:
        filter_items = dict(FILTER_ITEMS)
        filter_by = dict(FILTER_BY)

        for filter_item in filter_list:
            active_filters.append(dict(
            filter_field=filter_items[filter_item['field']],
            filter_by=filter_by[int(filter_item['filter'])],
            filter_value=filter_item['value']))


def get_processes(process_name):
    "Gets running processes by process name"
    pipe1 = subprocess.Popen(['ps', 'ax'], stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
    pipe2 = subprocess.Popen(['grep', '-i', process_name], stdin=pipe1.stdout,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pipe1.stdout.close()
    processes = pipe2.communicate()[0]
    return len(processes.split('\n')[:-1])


def get_config_option(search_option):
    """
    Returns a MailScanner config setting from the
    config file
    """
    config = getattr(settings, 'MS_CONFIG',
    '/etc/MailScanner/MailScanner.conf')
    quickpeek = getattr(settings, 'MS_QUICKPEEK', '/usr/sbin/Quick.Peek')
    cmd = "%s '%s' %s" % (quickpeek, search_option, config)

    pipe1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    val = pipe1.communicate()[0]
    return val.strip()


def host_is_local(host):
    """
    Checks if host is local to host running the function
    """
    host_name = socket.gethostbyname(host)
    ip_addr = socket.gethostbyname(socket.gethostname())
    if host_name in [ip_addr, '127.0.0.1']:
        return True
    else:
        return False


def get_sys_status(request):
    "Returns system status"
    import os
    from baruwa.messages.models import MessageStats
    from baruwa.status.models import MailQueueItem

    addrs = []
    act = 3

    inq = MailQueueItem.objects.filter(direction=1)
    outq = MailQueueItem.objects.filter(direction=2)
    if not request.user.is_superuser:
        addrs = request.session['user_filter']['addresses']
        act = request.session['user_filter']['account_type']
        if act == 2:
            query = Q()
            for addr in addrs:
                atdomain = "@%s" % addr
                query = query | Q(Q(**{'from_address__iendswith': atdomain}) |
                                Q(**{'to_address__iendswith': atdomain}))
            inq = inq.filter(query)
            outq = outq.filter(query)
        if act == 3:
            inq = inq.filter(Q(from_address__in=addrs) |
                                Q(to_address__in=addrs))
            outq = outq.filter(Q(from_address__in=addrs) |
                                Q(to_address__in=addrs))

    data = MessageStats.objects.get(request.user, addrs, act)

    inq = inq.aggregate(count=Count('messageid'))
    outq = outq.aggregate(count=Count('messageid'))
    #icount = inq['count']
    #ocount = outq['count']

    val1, val2, val3 = os.getloadavg()

    scanners = get_processes('MailScanner')
    mas = get_config_option('MTA')
    mta = get_processes(mas)
    clamd = get_processes('clamd')

    if 0 in [scanners, mta, clamd] or val1 > 10:
        status = False
    else:
        status = True

    try:
        spam = data.spam_mail + data.high_spam
    except TypeError:
        spam = 0

    return dict(baruwa_status=status, baruwa_mail_total=data.total,
    baruwa_spam_total=spam, baruwa_virus_total=data.virii or 0,
    baruwa_in_queue=inq['count'], baruwa_out_queue=outq['count'])


def geoip_lookup(ipaddr):
    try:
        if IP(ipaddr).version() == 6:
            gip = GeoIP.open(settings.GEOIP_IPV6_DB, GeoIP.GEOIP_MEMORY_CACHE)
            country_code = gip.country_code_by_addr_v6(ipaddr).lower()
            country_name = gip.country_name_by_name_v6(ipaddr)
        else:
            gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
            country_code = gip.country_code_by_addr(ipaddr).lower()
            country_name = gip.country_name_by_addr(ipaddr)
        return country_name, country_code
    except (GeoIP.error, AttributeError):
        return ('', '')


def ipaddr_is_valid(ip):
    """
    Checks the validity of an IP address
    """
    try:
        IP(ip)
        return True
    except ValueError:
        return False
