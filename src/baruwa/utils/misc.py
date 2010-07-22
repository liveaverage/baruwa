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

from django.template.defaultfilters import force_escape
from django.conf import settings
from django.db.models import Q

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

def to_dict(tuple_list):
    d = {}
    for i in tuple_list:
      d[i[0]] = i[1] 
    return d
      
def apply_filter(model, request, active_filters):
    if request.session.get('filter_by', False):
        filter_list = request.session.get('filter_by')
        model = gen_dynamic_query(model,filter_list,active_filters)
    return model
    
def gen_dynamic_query(model, filter_list, active_filters=None):
    from baruwa.reports.forms import FilterForm,FILTER_ITEMS,FILTER_BY
    kwargs = {}
    lkwargs = {}
    nkwargs = {}
    lnkwargs = {}
    nargs = []
    largs = []
    filter_items = to_dict(list(FILTER_ITEMS))
    filter_by = to_dict(list(FILTER_BY))
    for filter_item in filter_list:
        if filter_item['filter'] == 1:
            tmp = "%s__exact" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
                    kwargs.update(kw)
        if filter_item['filter'] == 2:
            tmp = "%s__exact" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                lnkwargs.update(kw)
                del nkwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lnkwargs.has_key(tmp):
                    nargs.append(Q(**kw))
                else:
			        nkwargs.update(kw)
        if filter_item['filter'] == 3:
            tmp = "%s__gt" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
                    kwargs.update(kw)
        if filter_item['filter'] == 4:
            tmp = "%s__lt" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
                    kwargs.update(kw)
        if filter_item['filter'] == 5:
            tmp = "%s__icontains" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
			        kwargs.update(kw)
        if filter_item['filter'] == 6:
            tmp = "%s__icontains" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                lnkwargs.update(kw)
                del nkwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lnkwargs.has_key(tmp):
                    nargs.append(Q(**kw))
                else:
			        nkwargs.update(kw)
        if filter_item['filter'] == 7:
            tmp = "%s__regex" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
			        kwargs.update(kw)
        if filter_item['filter'] == 8:
            tmp = "%s__regex" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                lnkwargs.update(kw)
                del nkwargs[tmp]
            else:
                kw = {str(tmp):str(filter_item['value'])}
                if lnkwargs.has_key(tmp):
                    nargs.append(Q(**kw))
                else:
			        nkwargs.update(kw)
        if filter_item['filter'] == 9:
            tmp = "%s__isnull" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str('True')}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str('True')}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
			        kwargs.update(kw)
        if filter_item['filter'] == 10:
            tmp = "%s__isnull" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str('True')}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                lnkwargs.update(kw)
                del nkwargs[tmp]
            else:
                kw = {str(tmp):str('True')}
                if lnkwargs.has_key(tmp):
                    nargs.append(Q(**kw))
                else:
			        nkwargs.update(kw)
        if filter_item['filter'] == 11:
            tmp = "%s__gt" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str('0')}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str('0')}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
			        kwargs.update(kw)
        if filter_item['filter'] == 12:
            tmp = "%s__exact" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str('0')}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                lkwargs.update(kw)
                del kwargs[tmp]
            else:
                kw = {str(tmp):str('0')}
                if lkwargs.has_key(tmp):
                    largs.append(Q(**kw))
                else:
			        kwargs.update(kw)
        if not active_filters is None:
			active_filters.append({'filter_field':filter_items[filter_item['field']],
                'filter_by':filter_by[int(filter_item['filter'])],'filter_value':filter_item['value']})
    if kwargs:
        model = model.filter(**kwargs)
    if nkwargs:
        model = model.exclude(**nkwargs)
    if nargs:
        q = Q()
        for query in nargs:
            q = q | query
        model = model.exclude(q)
    if largs:
        q = Q()
        for query in largs:
            q = q | query
        model = model.filter(q)
    return model

def raw_user_filter(request):
    dsql = []
    esql = []
    sql = '1 != 1'
    if not request.user.is_superuser:
        addresses = request.session['user_filter']['addresses']
        account_type = request.session['user_filter']['account_type']
        if account_type == 2:
            if addresses:
                for domain in addresses:
                    dsql.append('to_domain="'+domain+'"')
                    dsql.append('from_domain="'+domain+'"')
                sql = ' OR '.join(dsql)
        if account_type == 3:
            if addresses:
                for email in addresses:
                    esql.append('to_address="'+email+'"')
                    esql.append('from_address="'+email+'"')
                esql.append('to_address="'+request.user.username+'"')
                sql = ' OR '.join(esql)
            else:
                sql = 'to_address="%s"' % request.user.username
        return '(' + sql +')'
        
def get_processes(process_name):
    import subprocess
    p1 = subprocess.Popen('ps ax',shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen('grep -i '+process_name, shell=True, stdin=p1.stdout,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p3 = subprocess.Popen('grep -v grep',shell=True, stdin=p2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p4 = subprocess.Popen('wc -l',shell=True, stdin=p3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes = p4.stdout.read()
    processes = int(processes.strip())
    return processes
    
def get_config_option(search_option):
    """
    Returns a MailScanner config setting from the
    config file
    """
    import os 
    config = getattr(settings, 'MS_CONFIG', '/etc/MailScanner/MailScanner.conf')
    COMMENT_CHAR = '#'
    OPTION_CHAR =  '='
    value = ''
    if os.path.exists(config):
        f = open(config)
        for line in f:
            if COMMENT_CHAR in line:
                line, comment = line.split(COMMENT_CHAR, 1)
            if OPTION_CHAR in line:
                option, value = line.split(OPTION_CHAR, 1)
                option = option.strip()
                value = value.strip()
                if search_option == option:
                    break
        f.close()
    return value