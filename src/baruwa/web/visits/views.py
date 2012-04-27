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

from django.conf import settings
from django.template import RequestContext
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required

from baruwa.web.visits.models import Traffic, Urlfilterdeny, Virusdetection, Searchquery
from baruwa.utils.decorators import onlysuperusers


@login_required
@onlysuperusers
def index(request, list_all=0, page=1, view_type='full', direction='dsc',
        order_by='id'):
    """index"""
    template_name = 'web/visits/index.html'
    active_filters = {}
    num_of_recent_visits = getattr(settings, 'BARUWA_NUM_RECENT_MESSAGES', 50)
    ordering = order_by
    if direction == 'dsc':
        ordering = order_by
        order_by = '-%s' % order_by

    if not list_all:
        last_id = request.META.get('HTTP_X_LAST_ID', None)
        if not last_id is None:
            last_id = last_id.strip()
            if not re.match(r'^(\d+)$', last_id):
                last_id = None
        if not last_id is None and request.is_ajax():
            visit_list = Traffic.objects\
                        .filter(id__gt=last_id)\
                        .all()[:num_of_recent_visits]
        else:
            visit_list = Traffic.objects.all()[:num_of_recent_visits]
    else:
        visit_list = Traffic.objects.order_by(order_by)
        if view_type == 'url':
            inner_q = Urlfilterdeny.objects.values('traffic').query
            visit_list = visit_list.filter(id__in=inner_q)
        if view_type == 'virus':
            inner_q = Virusdetection.objects.values('traffic').query
            visit_list = visit_list.filter(id__in=inner_q)
        if view_type == 'search':
            inner_q = Searchquery.objects.values('traffic').query
            visit_list = visit_list.filter(id__in=inner_q)
        visit_list = visit_list.all()
    # visit_list = apply_filter(visit_list, request, active_filters)
    
    if request.is_ajax():
        # sys_status = jsonify_status(status(request))
        sys_status = None
        if not list_all:
            visit_list = map(jsonify_msg_list, visit_list)
            pg = None
        else:
            p = Paginator(visit_list, num_of_recent_visits)
            if page == 'last':
                page = p.num_pages
            po = p.page(page)
            visit_list = po.object_list
            # visit_list = map(jsonify_msg_list, visit_list)
            page = int(page)
            ap = 2
            startp = max(page - ap, 1)
            if startp <= 3:
                startp = 1
            endp = page + ap + 1
            pn = [n for n in range(startp, endp) if n > 0 and n <= p.num_pages]
            pg = {'page': page, 'pages': p.num_pages, 'page_numbers': pn,
            'next': po.next_page_number(), 'previous': po.previous_page_number(),
            'has_next': po.has_next(), 'has_previous': po.has_previous(),
            'show_first': 1 not in pn, 'show_last': p.num_pages not in pn,
            'view_type': view_type, 'direction': direction, 'order_by': ordering}
        json = anyjson.dumps({'items': visit_list, 'paginator': pg,
                                'status': sys_status})
        return HttpResponse(json, mimetype='application/javascript')
    if list_all:
        return object_list(request, template_name=template_name,
        queryset=visit_list, paginate_by=num_of_recent_visits, page=page,
        extra_context={'view_type': view_type, 'direction': direction,
        'order_by': ordering, 'active_filters': active_filters,
        'list_all': list_all, 'app': 'web/visits/' + view_type}, allow_empty=True)
    else:
        return object_list(request, template_name=template_name,
        queryset=visit_list, extra_context={'view_type': view_type,
        'direction': direction, 'order_by': ordering,
        'active_filters': active_filters, 'list_all': list_all})


@login_required
@onlysuperusers
def detail(request, visit_id):
    """
    Displays details of a visit
    """
    visit_details = get_object_or_404(Traffic, id=visit_id)
    return render_to_response('web/visits/detail.html', locals(),
        context_instance=RequestContext(request))
