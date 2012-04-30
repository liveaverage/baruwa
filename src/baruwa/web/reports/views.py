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

import anyjson

from django.template import RequestContext
from django.db.models import Count, Max, Min
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.db import IntegrityError, DatabaseError
from django.template.defaultfilters import force_escape
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from baruwa.web.visits.models import Traffic
from baruwa.web.reports.forms import FilterForm
from baruwa.utils.decorators import onlysuperusers
from baruwa.web.reports.models import WebSavedFilter
from baruwa.web.reports.forms import FilterForm, FILTER_ITEMS, FILTER_BY
from baruwa.web.reports.utils import run_query, pack_json_data, REPORT_DICT
from baruwa.utils.queryfilters import gen_dynamic_query, get_active_filters


@login_required
@onlysuperusers
def index(request, list_all=0, page=1):
    """index"""
    errors = ''
    success = True
    active_filters = []
    saved_filters = []
    data = Traffic.objects
    filters = WebSavedFilter.objects.all().filter(user=request.user)
    filter_form = FilterForm()
    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            cleaned_data = filter_form.cleaned_data
            in_field = force_escape(cleaned_data['filtered_field'])
            in_value = force_escape(cleaned_data['filtered_value'])
            in_filtered_by = int(cleaned_data['filtered_by'])
            if not request.session.get('web_filter_by', False):
                request.session['web_filter_by'] = []
                request.session['web_filter_by'].append(
                    {'field': in_field, 'filter': in_filtered_by,
                    'value': in_value})
            else:
                fitem = {'field': in_field, 'filter': in_filtered_by,
                    'value': in_value}
                if not fitem in request.session['web_filter_by']:
                    request.session['web_filter_by'].append(fitem)
                    request.session.modified = True
                else:
                    success = False
                    errors = _("The requested filter is already being used")
            filter_list = request.session.get('web_filter_by')
            data = gen_dynamic_query(data, filter_list, active_filters, True)
        else:
            success = False
            error_list = filter_form.errors.values()[0]
            errors = error_list[0]
            if request.session.get('web_filter_by', False):
                filter_list = request.session.get('web_filter_by')
                data = gen_dynamic_query(data, filter_list, active_filters, True)
    else:
        if request.session.get('web_filter_by', False):
            filter_list = request.session.get('web_filter_by')
            data = gen_dynamic_query(data, filter_list, active_filters, True)
    data = data.aggregate(count=Count('date'), newest=Max('date'), oldest=Min('date'))
    if filters.count() > 0:
        if request.session.get('web_filter_by', False):
            filter_list = request.session.get('web_filter_by')
        else:
            filter_list = []
        for filt in filters:
            loaded = 0
            if filter_list:
                loaded = 0
                for fitem in filter_list:
                    if fitem['filter'] == filt.op_field and (
                        fitem['value'] == filt.value and
                        fitem['field'] == filt.field):
                        loaded = 1
                        break
            saved_filters.append(
                {'filter_id': filt.id, 'filter_name': force_escape(filt.name),
                'is_loaded': loaded})
    if request.is_ajax():
        if not data['newest'] is None and not data['oldest'] is None:
            data['newest'] = data['newest'].strftime("%a %d %b %Y @ %H:%M %p")
            data['oldest'] = data['oldest'].strftime("%a %d %b %Y @ %H:%M %p")
        else:
            data['newest'] = ''
            data['oldest'] = ''
        response = anyjson.dumps({'success': success, 'data': data,
            'errors': errors, 'active_filters': active_filters,
            'saved_filters': saved_filters})
        return HttpResponse(response,
            content_type='application/javascript; charset=utf-8')

    return render_to_response('web/reports/index.html', {'form': filter_form,
        'data': data, 'errors': errors, 'active_filters': active_filters,
        'saved_filters': saved_filters},
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def rem_filter(request, index_num):
    "removes filter"
    if request.session.get('web_filter_by', False):
        try:
            fil = request.session.get('web_filter_by')
            fil.remove(fil[int(index_num)])
            request.session.modified = True
        except AttributeError:
            pass
        if request.is_ajax():
            return index(request)
    return HttpResponseRedirect(reverse('web-reports-index'))


@login_required
@onlysuperusers
def save_filter(request, index_num):
    "saves filter"
    error_msg = ''
    if request.session.get('web_filter_by', False):
        filter_items = dict(FILTER_ITEMS)
        filter_by = dict(FILTER_BY)

        filters = request.session.get('web_filter_by')
        filt = filters[int(index_num)]
        name = (filter_items[filt["field"]] + " " + 
        filter_by[int(filt["filter"])] + " " + filt["value"])
        fil = WebSavedFilter(name=name,
                        field=filt["field"],
                        op_field=filt["filter"],
                        value=filt["value"],
                        user=request.user)
        try:
            fil.save()
        except IntegrityError:
            error_msg = _('This filter already exists')
        if request.is_ajax():
            if error_msg == '':
                return index(request)
            else:
                response = anyjson.dumps(
                    {'success': False, 'data': [], 'errors': error_msg,
                    'active_filters': [], 'saved_filters': []})
                return HttpResponse(response,
                    content_type='application/javascript; charset=utf-8')
    return HttpResponseRedirect(reverse('web-reports-index'))


@login_required
@onlysuperusers
def load_filter(request, index_num):
    "loads a filter"
    try:
        filt = WebSavedFilter.objects.get(id=int(index_num))
        if not request.session.get('web_filter_by', False):
            request.session['web_filter_by'] = []
            request.session['web_filter_by'].append(
                {'field': filt.field, 'filter': filt.op_field,
                'value': filt.value})
        else:
            fitem = {'field': filt.field, 'filter': filt.op_field,
                'value': filt.value}
            if not fitem in request.session['web_filter_by']:
                request.session['web_filter_by'].append(fitem)
                request.session.modified = True
        if request.is_ajax():
            return index(request)
        else:
            return HttpResponseRedirect(reverse('web-reports-index'))
    except WebSavedFilter.DoesNotExist:
        error_msg = _('This filter you attempted to load does not exist')
        if request.is_ajax():
            response = anyjson.dumps({'success': False, 'data': [],
                'errors': error_msg, 'active_filters': [],
                'saved_filters': []})
            return HttpResponse(response,
                content_type='application/javascript; charset=utf-8')
        else:
            return HttpResponseRedirect(reverse('web-reports-index'))


@login_required
@onlysuperusers
def del_filter(request, index_num):
    "deletes a filter"
    try:
        filt = WebSavedFilter.objects.get(id=int(index_num))
    except WebSavedFilter.DoesNotExist:
        error_msg = _('This filter you attempted to delete does not exist')
        if request.is_ajax():
            response = anyjson.dumps({'success': False,
                'data': [], 'errors': error_msg, 'active_filters': [],
                'saved_filters': []})
            return HttpResponse(response,
                content_type='application/javascript; charset=utf-8')
        else:
            return HttpResponseRedirect(reverse('web-reports-index'))
    else:
        try:
            filt.delete()
        except DatabaseError:
            error_msg = _('Deletion of the filter failed, Try again')
            if request.is_ajax():
                response = anyjson.dumps({'success': False, 'data': [],
                    'errors': error_msg, 'active_filters': [],
                    'saved_filters': []})
                return HttpResponse(response,
                    content_type='application/javascript; charset=utf-8')
        if request.is_ajax():
            return index(request)
        else:
            return HttpResponseRedirect(reverse('web-reports-index'))


@login_required
@onlysuperusers
def report(request, report_kind):
    "displays a report"
    report_kind = int(report_kind)
    report_title = REPORT_DICT[report_kind]['title']
    template = "web/reports/piereport.html"
    active_filters = []
    data = run_query(report_kind, request, active_filters)
    pie_data = pack_json_data(data, report_kind)
    filter_form = FilterForm()

    if request.is_ajax():
        response = anyjson.dumps({'items': list(data), 'pie_data': pie_data})
        return HttpResponse(response,
            content_type='application/javascript; charset=utf-8')
    else:
        pie_data = anyjson.dumps(pie_data)
        return render_to_response(template, {'pie_data': pie_data,
            'top_items': data, 'report_title': report_title,
            'report_kind': report_kind, 'active_filters': active_filters,
            'form': filter_form}, context_instance=RequestContext(request))

