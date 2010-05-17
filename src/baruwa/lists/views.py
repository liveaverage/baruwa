#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# vim: ai ts=4 sts=4 et sw=4
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.db import IntegrityError
from django.forms.util import ErrorList as errorlist
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from baruwa.lists.models import Blacklist, Whitelist
from baruwa.lists.forms import ListAddForm, FilterForm, UserListAddForm, ListDeleteForm
from baruwa.accounts.models import User
import re

def json_ready(element):
    element['id'] = str(element['id'])
    element['from_address'] = force_escape(element['from_address'])
    element['to_address'] = force_escape(element['to_address'])
    return element

@never_cache
@login_required
def index(request,list_kind=1,page=1,direction='dsc',order_by='id',search_for='',query_type=3):
    list_kind = int(list_kind)
    user_type = request.session['user_filter']['user_type']
    query_type = int(query_type)
    if query_type == 3:
        query_type = None
    ordering = order_by
    if search_for == '':
        do_filtering = False
    else:
        do_filtering = True
    
    if direction == 'dsc':
        ordering = order_by
        order_by = "-%s" % order_by

    if list_kind == 1:
        listing = Whitelist.objects.values('id','to_address','from_address').order_by(order_by)
    elif list_kind == 2:
        listing = Blacklist.objects.values('id','to_address','from_address').order_by(order_by)

    form = ListAddForm(request)
    
    if not request.user.is_superuser:
        q = Q()
        addresses = request.session['user_filter']['filter_addresses']
        if user_type == 'D':
            if addresses:
                for domain in addresses:
                    kw = {'to_address__iendswith':domain.filter}
                    q = q | Q(**kw)
                listing = listing.filter(q)
            else:
                listing = listing.filter(to_address__iendswith='example.net')
        if user_type == 'U':
            form = UserListAddForm(request)
            if addresses:
                for email in addresses:
                   kw = {'to_address__exact':email.filter}
                   q = q | Q(**kw)
                kw = {'to_address__exact':request.user.username}
                q = q | Q(**kw)
                listing = listing.filter(q)
            else:
                listing = listing.filter(to_address__exact=request.user.username)

    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            query_type = int(filter_form.cleaned_data['query_type'])
            search_for = filter_form.cleaned_data['search_for']
            if search_for != "" and not search_for is None:
                do_filtering = True
    if do_filtering:
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
    app = "lists/%d" % list_kind
    if request.is_ajax():
        p = Paginator(listing,20)
        if page == 'last':
            page = p.num_pages
        po = p.page(page)
        listing = po.object_list
        listing = map(json_ready,listing)
        page = int(page)
        ap = 2
        sp = max(page - ap, 1)
        if sp <= 3: sp = 1
        ep = page + ap + 1
        pn = [n for n in range(sp,ep) if n > 0 and n <= p.num_pages]
        pg = {'page':page,'pages':p.num_pages,'page_numbers':pn,'next':po.next_page_number(),'previous':po.previous_page_number(),
        'has_next':po.has_next(),'has_previous':po.has_previous(),'show_first':1 not in pn,'show_last':p.num_pages not in pn,
        'app':app,'list_kind':list_kind,'direction':direction,'order_by':ordering,'search_for':search_for,'query_type':query_type}
        json = simplejson.dumps({'items':listing,'paginator':pg})
        return HttpResponse(json, mimetype='application/javascript')
    else:
        return object_list(request,template_name='lists/index.html',queryset=listing, paginate_by=20,page=page,
            extra_context={'app':app,'list_kind':list_kind,'direction':direction,'order_by':ordering,'search_for':search_for,'query_type':query_type,'list_all':0,
            'form':form})

@login_required
def add_to_list(request):
    template = 'lists/add.html'
    error_msg = ''
    user_type = request.session['user_filter']['user_type']

    if request.method == 'GET':
        if user_type == 'U':
            form = UserListAddForm(request)
        else:
            form = ListAddForm(request) 
    elif request.method == 'POST':
        if user_type == 'U':
            form = UserListAddForm(request, request.POST)
        else:
            form = ListAddForm(request, request.POST) 
        if form.is_valid():
            clean_data = form.cleaned_data
            if user_type != 'U':
                if clean_data['to_domain'] != '' and clean_data['to_address'] != 'default':
                    to = "%s@%s" % (force_escape(clean_data['to_address']), force_escape(clean_data['to_domain']))
                elif clean_data['to_domain'] != '' and clean_data['to_address'] == 'default':
                    to = force_escape(clean_data['to_domain'])
                else:
                    to = force_escape(clean_data['to_address'])
            else:
                to = clean_data['to_address']
            if not request.user.is_superuser:
                addresses = request.session['user_filter']['filter_addresses']
                a = [address.filter for address in addresses]
                if user_type == 'D':
                    if clean_data['to_domain'] not in a:
                        return HttpResponseForbidden('You do not have authorization')
                if user_type == 'U':
                    if to != request.user.username:
                        if to not in a:
                            return HttpResponseForbidden('You do not have authorization')
            kwargs = {'to_address':to,'from_address':clean_data['from_address']}
            lt = int(clean_data['list_type'])
            if lt == 1:
                try:
                    b = Blacklist.objects.get(**kwargs)
                    error_msg = '%s is blacklisted, please remove from blacklist before attempting to whitelist' % force_escape(clean_data['from_address'])
                except Blacklist.DoesNotExist:
                    wl = Whitelist(to_address=to,from_address=clean_data['from_address'])
                    try:
                        wl.save()
                    except IntegrityError:
                        error_msg = 'The list item already exists'
                    except:
                        error_msg = 'Unknown error occured'
            else:
                try:
                    w = Whitelist.objects.get(**kwargs)
                    error_msg = '%s is whitelisted, please remove from whitelist before attempting to blacklist' % force_escape(clean_data['from_address'])
                except Whitelist.DoesNotExist:    
                    bl = Blacklist(to_address=to,from_address=clean_data['from_address'])
                    try:
                        bl.save()
                    except IntegrityError:
                        error_msg = 'The list item already exists'
                    except:
                        error_msg = 'Unknown error occured'

            if request.is_ajax():
                if error_msg == '':
                    request.method = 'GET'
                    return index(request,int(clean_data['list_type']),1,'dsc','id','',3)
                else:
                    json = simplejson.dumps({'items':[],'paginator':[],'error':error_msg})
                    return HttpResponse(json,mimetype='application/javascript')
            else:
                return HttpResponseRedirect(reverse('lists-start', args=[lt]))
        else:
            if request.is_ajax():
                error_list = form.errors.values()[0]
                html = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]) #form.errors
                response = simplejson.dumps({'error': unicode(error_list[0]),'form_field':html.keys()[0]})
                return HttpResponse(response,mimetype='application/javascript')
    return render_to_response(template, {'form':form}, context_instance=RequestContext(request))

@never_cache
@login_required
def delete_from_list(request, list_kind=0, item_id=0):
    if request.method == 'POST':
        form = ListDeleteForm(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data['list_item']
            list_kind = form.cleaned_data['list_kind']
        else:
            error_list = form.errors.values()[0]
            return HttpResponse('Error occured while deleting the item')

    item_id = int(item_id)
    list_kind = int(list_kind)
    error_msg = ''

    if list_kind == 1:
        list = Whitelist
    else:
        list = Blacklist

    list_item = get_object_or_404(list, pk=item_id)
    if not list_item.can_access(request):
        return HttpResponseForbidden('You do not have authorization')

    if request.method == 'POST':
        list_item.delete()
        if request.is_ajax():
            if error_msg == '':
                page = 1
                direction = 'dsc'
                order_by = 'id'
                params = request.META.get('HTTP_X_LIST_PARAMS', None)
                if params:
                    g = re.match(r"^lists\-([1-2])\-([0-9]+)\-(dsc|asc)\-(id|to_address|from_address)$",params)
                    if g:
                        list_kind, page, direction, order_by = g.groups()
                request.method = 'GET'
                return index(request, list_kind, page, direction, order_by, '', 3)
            else:
                json = simplejson.dumps({'items':[],'paginator':[],'error':error_msg})
            return HttpResponse(json, mimetype='application/javascript')
        else:
            return HttpResponseRedirect(reverse('lists-start', args=[list_kind]))
    else:
        if request.is_ajax():
            return HttpResponseRedirect(reverse('lists-index'))
        else:
            form = ListDeleteForm()
            form.fields['list_kind'].widget.attrs['value'] = list_kind
            form.fields['list_item'].widget.attrs['value'] = list_item.id
            return render_to_response('lists/delete.html', {'item':list_item, 'form':form}, context_instance=RequestContext(request))
