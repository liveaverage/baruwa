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

from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.template.defaultfilters import force_escape
from django.template import RequestContext
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.utils.translation import ugettext as _
from baruwa.lists.forms import ListAddForm, AdminListAddForm
from baruwa.lists.forms import FilterForm, ListDeleteForm
from baruwa.lists.models import List
from baruwa.utils.misc import jsonify_list

@login_required
def index(request, list_kind=1, page=1, direction='dsc', order_by='id'):
    """index"""
    
    if request.user.is_superuser:
        account_type = 1
    else:
        account_type = request.session['user_filter']['account_type']
    
    list_kind = int(list_kind)
    ordering = order_by
    filter_active = False
    
    if direction == 'dsc':
        ordering = order_by
        order_by = "-%s" % order_by

    listing = List.objects.values('id', 'to_address', 'from_address').filter(
        list_type=list_kind).order_by(order_by)
    
    if not request.user.is_superuser:
        query = Q()
        addresses = request.session['user_filter']['addresses']
        if account_type == 2:
            if addresses:
                for domain in addresses:
                    kwarg = {'to_address__iendswith':domain}
                    query = query | Q(**kwarg)
                listing = listing.filter(query)
            else:
                listing = listing.filter(user=request.user.id)
        if account_type == 3:
            listing = listing.filter(user=request.user.id)
                
    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            request.session['query_type'] = int(
                filter_form.cleaned_data['query_type'])
            request.session['search_for'] = (
                filter_form.cleaned_data['search_for'])
            request.session.modified = True
            
    search_for = request.session.get('search_for', '')
    query_type = request.session.get('query_type', 1)
    
    if search_for != "":
        filter_active = True
        if query_type == 1:
            if ordering == 'to_address':
                listing = listing.filter(to_address__icontains=search_for)
            elif ordering == 'from_address':
                listing = listing.filter(from_address__icontains=search_for)
        else:
            if ordering == 'to_address':
                listing = listing.exclude(to_address__icontains=search_for)
            elif ordering == 'from_address':
                listing = listing.exclude(from_address__icontains=search_for)
    
    if request.is_ajax():
        p = Paginator(listing, 15)
        if page == 'last':
            page = p.num_pages
        po = p.page(page)
        listing = po.object_list
        listing = map(jsonify_list, listing)
        page = int(page)
        ap = 2
        sp = max(page - ap, 1)
        if sp <= 3:
            sp = 1
        ep = page + ap + 1
        pn = [n for n in range(sp, ep) if n > 0 and n <= p.num_pages]
        pg = {'page':page, 'pages':p.num_pages, 'page_numbers':pn, 
        'next':po.next_page_number(), 'previous':po.previous_page_number(),
        'has_next':po.has_next(), 'has_previous':po.has_previous(), 
        'show_first':1 not in pn, 'show_last':p.num_pages not in pn,
        'app': 'lists', 'list_kind':list_kind, 'direction':direction, 
        'order_by':ordering, 'filter_active':filter_active}
        json = simplejson.dumps({'items':listing, 'paginator':pg})
        return HttpResponse(json, mimetype='application/javascript')
            
    return object_list(request, template_name='lists/index.html', 
        queryset=listing, paginate_by=15, page=page, 
        extra_context={'app': 'lists', 'list_kind':list_kind, 
        'direction':direction, 'order_by':ordering, 
        'filter_active':filter_active, 'list_all':0})

@login_required
def add_to_list(request, template = 'lists/add.html'):
    """add_to_list"""
    error_msg = ''
    is_saved = False
    
    if not request.user.is_superuser:
        account_type = request.session['user_filter']['account_type']
    else:
        account_type = 1
    
    if request.method == 'GET':
        if account_type == 1 or account_type == 2:
            form = AdminListAddForm(request)
        else:
            form = ListAddForm(request) 
    elif request.method == 'POST':
        if account_type == 1 or account_type == 2:
            form = AdminListAddForm(request, request.POST)
        else:
            form = ListAddForm(request, request.POST)  
        if form.is_valid():
            clean_data = form.cleaned_data
            if account_type == 1 or account_type == 2:
                user_part = clean_data['user_part']
                to_address = clean_data['to_address']
                if user_part is None or user_part == '':
                    user_part = 'any'
                if to_address is None or to_address == '':
                    to_address = 'any'
                    
                if user_part != 'any' and to_address != 'any':
                    toaddr = "%s@%s" % (
                        force_escape(user_part), force_escape(to_address))
                elif user_part == 'any' and to_address != 'any':
                    toaddr = to_address
                else:
                    toaddr = to_address
            else:
                toaddr = clean_data['to_address']
            
            try:
                l = List(list_type=clean_data['list_type'], 
                    from_address=clean_data['from_address'], to_address=toaddr, 
                    user=request.user)
                l.save()
                is_saved = True
                if account_type == 1 or account_type == 2:
                    form = AdminListAddForm(request)
                else:
                    form = ListAddForm(request)
            except IntegrityError:
                error_msg = _('The list item already exists')
            except:
                error_msg = _('Error occured saving the list item')
                
            if request.is_ajax():
                response = simplejson.dumps({'success':is_saved, 
                    'error_msg':error_msg})
                return HttpResponse(response, 
                    content_type='application/javascript; charset=utf-8')
        else:
            if request.is_ajax():
                error_list = form.errors.values()[0]
                html = dict([(k, [unicode(e) for e in v]) 
                    for k, v in form.errors.items()]) #form.errors
                response = simplejson.dumps({'success':False, 
                    'error_msg': unicode(error_list[0]), 
                    'form_field':html.keys()[0]})
                return HttpResponse(response, 
                    content_type='application/javascript; charset=utf-8')
                    
    return render_to_response(template, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def delete_from_list(request, item_id):
    "delete filter"
    list_item = get_object_or_404(List, pk=item_id)
    if request.method == 'POST':
        form = ListDeleteForm(request.POST)
        if form.is_valid():
            if not list_item.can_access(request):
                return HttpResponseForbidden(_('You do not have authorization'))
            list_type = list_item.list_type
            list_item.delete()
            if request.is_ajax():
                response = simplejson.dumps({'success':True})
                return HttpResponse(response, 
                    content_type='application/javascript; charset=utf-8')
            return HttpResponseRedirect(reverse('lists-start', 
                args=[list_type]))
        else:
            if request.is_ajax():
                response = simplejson.dumps({'success':False})
                return HttpResponse(response, 
                    content_type='application/javascript; charset=utf-8')
    else:
        form = ListDeleteForm()
        form.fields['list_item'].widget.attrs['value'] = item_id
    return render_to_response('lists/delete.html', locals(), 
        context_instance=RequestContext(request))
    
@login_required
def rem_filter(request):
    "remove filter"
    try:
        del request.session['search_for']
        del request.session['query_type']
        request.session.modified = True  
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('lists-index'))
    