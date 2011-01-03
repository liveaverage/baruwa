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

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Count, Max, Min
from django.db import IntegrityError
from django.utils import simplejson
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.utils.translation import ugettext as _
from baruwa.reports.forms import FilterForm, FILTER_ITEMS, FILTER_BY
from baruwa.reports.models import SavedFilter
from baruwa.reports.utils import pack_json_data, run_query, run_hosts_query
from baruwa.messages.models import Message
from baruwa.utils.misc import gen_dynamic_query, get_active_filters

@login_required
def index(request):
    """index"""
    errors = ''
    success = True
    active_filters = []
    saved_filters = []
    data = Message.messages.for_user(request)
    filters = SavedFilter.objects.all().filter(user=request.user)
    filter_form = FilterForm()
    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            cleaned_data = filter_form.cleaned_data
            in_field = force_escape(cleaned_data['filtered_field'])
            in_value = force_escape(cleaned_data['filtered_value'])
            in_filtered_by = int(cleaned_data['filtered_by'])
            if not request.session.get('filter_by', False):
                request.session['filter_by'] = []
                request.session['filter_by'].append(
                    {'field':in_field, 'filter':in_filtered_by,
                    'value':in_value})
            else:
                fitem = {'field':in_field, 'filter':in_filtered_by,
                    'value':in_value}
                if not fitem in request.session['filter_by']:
                    request.session['filter_by'].append(fitem)
                    request.session.modified = True
                else:
                    success = False
                    errors = _("The requested filter is already being used")
            filter_list = request.session.get('filter_by')
            data = gen_dynamic_query(data, filter_list, active_filters)
        else:
            success = False
            error_list = filter_form.errors.values()[0]
            errors = error_list[0] #errorlist(error_list).as_ul()
            if request.session.get('filter_by', False):
                filter_list = request.session.get('filter_by')
                data = gen_dynamic_query(data, filter_list, active_filters)
    else:
        filter_form = FilterForm()
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            data = gen_dynamic_query(data, filter_list, active_filters)

    data = data.aggregate(count=Count('timestamp'), newest=Max('timestamp'),
        oldest=Min('timestamp'))
    if filters.count() > 0:
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
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
                {'filter_id':filt.id, 'filter_name':force_escape(filt.name),
                'is_loaded':loaded})

    if request.is_ajax():
        if not data['newest'] is None and not data['oldest'] is None:
            data['newest'] = data['newest'].strftime("%a %d %b %Y @ %H:%M %p")
            data['oldest'] = data['oldest'].strftime("%a %d %b %Y @ %H:%M %p")
        else:
            data['newest'] = ''
            data['oldest'] = ''
        response = simplejson.dumps({'success':success, 'data':data, 
            'errors':errors, 'active_filters':active_filters, 
            'saved_filters':saved_filters})
        return HttpResponse(response, 
            content_type='application/javascript; charset=utf-8')

    return render_to_response('reports/index.html', {'form':filter_form,
        'data':data, 'errors':errors, 'active_filters':active_filters,
        'saved_filters':saved_filters}, 
        context_instance=RequestContext(request))

@login_required
def rem_filter(request, index_num):
    "removes filter"
    if request.session.get('filter_by', False):
        try:
            fil = request.session.get('filter_by')
            fil.remove(fil[int(index_num)])
            request.session.modified = True
        except:
            pass
        if request.is_ajax():
            return index(request)
    return HttpResponseRedirect(reverse('reports-index'))


@login_required
def save_filter(request, index_num):
    "saves filter"
    error_msg = ''
    if request.session.get('filter_by', False):
        filter_items = dict(FILTER_ITEMS)
        filter_by = dict(FILTER_BY)

        filters = request.session.get('filter_by')
        filt = filters[int(index_num)]
        name = filter_items[filt["field"]]+" "
        +filter_by[int(filt["filter"])]+" "+filt["value"]
        fil = SavedFilter(name=name, field=filt["field"], 
        op_field=filt["filter"], value=filt["value"], 
        user=request.user)
        try:
            fil.save()
        except IntegrityError:
            error_msg = _('This filter already exists')
        if request.is_ajax():
            if error_msg == '':
                return index(request)
            else:
                response = simplejson.dumps(
                    {'success':False, 'data':[], 'errors':error_msg, 
                    'active_filters':[], 'saved_filters':[]})
                return HttpResponse(response, 
                    content_type='application/javascript; charset=utf-8')
    return HttpResponseRedirect(reverse('reports-index'))

@login_required
def load_filter(request, index_num):
    "loads a filter"
    try:
        filt = SavedFilter.objects.get(id=int(index_num))
        if not request.session.get('filter_by', False):
            request.session['filter_by'] = []
            request.session['filter_by'].append(
                {'field':filt.field, 'filter':filt.op_field, 
                'value':filt.value})
        else:
            fitem = {'field':filt.field, 'filter':filt.op_field, 
                'value':filt.value}
            if not fitem in request.session['filter_by']:
                request.session['filter_by'].append(fitem)
                request.session.modified = True
        if request.is_ajax():
            return index(request)
        else:
            return HttpResponseRedirect(reverse('reports-index'))
    except:
        error_msg = _('This filter you attempted to load does not exist')
        if request.is_ajax():
            response = simplejson.dumps({'success':False, 'data':[], 
                'errors':error_msg, 'active_filters':[], 'saved_filters':[]})
            return HttpResponse(response, 
                content_type='application/javascript; charset=utf-8')
        else:
            return HttpResponseRedirect(reverse('reports-index'))

@login_required
def del_filter(request, index_num):
    "deletes a filter"
    try:
        filt = SavedFilter.objects.get(id=int(index_num))
    except:
        error_msg = _('This filter you attempted to delete does not exist')
        if request.is_ajax():
            response = simplejson.dumps({'success':False, 
                'data':[], 'errors':error_msg, 'active_filters':[], 
                'saved_filters':[]})
            return HttpResponse(response, 
                content_type='application/javascript; charset=utf-8')
        else:
            return HttpResponseRedirect(reverse('reports-index'))
    else:
        try:
            filt.delete()
        except:
            error_msg = _('Deletion of the filter failed, Try again')
            if request.is_ajax():
                response = simplejson.dumps({'success':False, 'data':[], 
                    'errors':error_msg, 'active_filters':[], 
                    'saved_filters':[]})
                return HttpResponse(response, 
                    content_type='application/javascript; charset=utf-8')
        if request.is_ajax():
            return index(request)
        else:
            return HttpResponseRedirect(reverse('reports-index'))

@login_required
def report(request, report_kind):
    "displays a report"
    report_kind = int(report_kind)
    template = "reports/piereport.html"
    active_filters = []
    if report_kind == 1:
        data = run_query('from_address', {'from_address__exact':""}, 
            '-num_count', request, active_filters)
        pie_data = pack_json_data(data, 'from_address', 'num_count')
        report_title = _("Top senders by quantity")
    elif report_kind == 2:
        data = run_query('from_address', {'from_address__exact':""}, 
            '-total_size', request, active_filters)
        pie_data = pack_json_data(data, 'from_address', 'total_size')
        report_title = _("Top senders by volume")
    elif report_kind == 3:
        data = run_query('from_domain', {'from_domain__exact':""}, 
            '-num_count', request, active_filters)
        pie_data = pack_json_data(data, 'from_domain', 'num_count')
        report_title = _("Top sender domains by quantity")
    elif report_kind == 4:
        data = run_query('from_domain', {'from_domain__exact':""}, 
            '-total_size', request, active_filters)
        pie_data = pack_json_data(data, 'from_domain', 'total_size')
        report_title = _("Top sender domains by volume")
    elif report_kind == 5:
        data = run_query('to_address', {'to_address__exact':""}, 
            '-num_count', request, active_filters)
        pie_data = pack_json_data(data, 'to_address', 'num_count')
        report_title = _("Top recipients by quantity")
    elif report_kind == 6:
        data = run_query('to_address', {'to_address__exact':""}, 
            '-total_size', request, active_filters)
        pie_data = pack_json_data(data, 'to_address', 'total_size')
        report_title = _("Top recipients by volume")
    elif report_kind == 7:
        data = run_query('to_domain', {'to_domain__exact':"", 
            'to_domain__isnull':False}, '-num_count', request, active_filters)
        pie_data = pack_json_data(data, 'to_domain', 'num_count')
        report_title = _("Top recipient domains by quantity")
    elif report_kind == 8:
        data = run_query('to_domain', {'to_domain__exact':"", 
            'to_domain__isnull':False}, '-total_size', request, active_filters)
        pie_data = pack_json_data(data, 'to_domain', 'total_size')
        report_title = _("Top recipient domains by volume")
    elif report_kind == 9:
        from baruwa.messages.models import SpamScores

        filter_list = []
        addrs = []
        counts = []
        scores = []
        act = 3

        if not request.user.is_superuser:
            addrs = request.session['user_filter']['addresses']
            act = request.session['user_filter']['account_type']

        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            get_active_filters(filter_list, active_filters)

        data = SpamScores.objects.all(request.user, filter_list, addrs, act)
        for row in data:
            scores.append(int(row.score))
            counts.append(int(row.count))

        if request.is_ajax():
            data = [obj.obj_to_dict() for obj in data]

        pie_data = {'scores':scores, 'count':counts}
        template = "reports/barreport.html"
        report_title = _("Spam Score distribution")
    elif report_kind == 10:
        data = run_hosts_query(request, active_filters)
        pie_data = pack_json_data(data, 'clientip', 'num_count')
        if request.is_ajax():
            from baruwa.messages.templatetags.messages_extras import \
                tds_geoip, tds_hostname
            for row in data:
                row['country'] = tds_geoip(row['clientip'])
                row['hostname'] = tds_hostname(row['clientip'])
        report_title = _("Top mail hosts by quantity")
        template = "reports/relays.html"
    elif report_kind == 11:
        from baruwa.messages.models import MessageTotals

        filter_list = []
        addrs = []
        dates = []
        mail_total = []
        spam_total = []
        virus_total = []
        size_total = []
        act = 3

        if not request.user.is_superuser:
            addrs = request.session['user_filter']['addresses']
            act = request.session['user_filter']['account_type']

        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            get_active_filters(filter_list, active_filters)

        data = MessageTotals.objects.all(request.user, filter_list, addrs, act)

        for row in data:
            dates.append(str(row.date))
            mail_total.append(int(row.mail_total))
            spam_total.append(int(row.spam_total))
            virus_total.append(int(row.virus_total))
            size_total.append(int(row.size_total))

        pie_data = {'dates':dates, 
                    'mail':mail_total, 
                    'spam':spam_total, 
                    'virii':virus_total, 
                    'mail_total':sum(mail_total), 
                    'spam_total':sum(spam_total), 
                    'virus_total':sum(virus_total), 
                    'volume_total':sum(size_total)}
        try:
            vpct = "%.1f" % ((1.0 * sum(virus_total)/sum(mail_total))*100)
            spct = "%.1f" % ((1.0 * sum(spam_total)/sum(mail_total))*100)
        except ZeroDivisionError:
            vpct = "0.0"
            spct = "0.0"
        pie_data['vpct'] = vpct
        pie_data['spct'] = spct
        #graph_totals = {}
        if request.is_ajax():
            data = [obj.obj_to_dict() for obj in data]

        report_title = _("Total messages [ After SMTP ]")
        template = "reports/listing.html"
    filter_form = FilterForm()

    if request.is_ajax():
        response = simplejson.dumps({'items':list(data), 'pie_data':pie_data})
        return HttpResponse(response, 
            content_type='application/javascript; charset=utf-8')
    else:
        if not report_kind in [9, 11]:
            pie_data = simplejson.dumps(pie_data)
        return render_to_response(template, {'pie_data':pie_data, 
            'top_items':data, 'report_title':report_title, 
            'report_kind':report_kind, 'active_filters':active_filters, 
            'form':filter_form}, context_instance=RequestContext(request))
