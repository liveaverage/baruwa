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
from django.shortcuts import render_to_response
from django.views.generic.list_detail import object_list
from django.db.models import Q
from baruwa.lists.models import Blacklist, Whitelist
from baruwa.lists.forms import ListAddForm,FilterForm,UserListAddForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator
from django.utils import simplejson
from django.db import IntegrityError
from django.forms.util import ErrorList as errorlist
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from baruwa.accounts.models import Users
import re

def json_ready(element):
    element['id'] = str(element['id'])
    return element

@never_cache
@login_required
def index(request,list_kind=1,page=1,direction='dsc',order_by='id',search_for='',query_type=3):
    list_kind = int(list_kind)
    load_domain = []
    load_email = []
    user_type = 'A'
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

    if not request.user.is_superuser:
        q = Q()
        user_type = request.session['user_filter']['user_type']
        addresses = request.session['user_filter']['filter_addresses']
        if user_type == 'D':
            if addresses:
                for domain in addresses:
                    load_domain.append(domain.filter)
                    kw = {'to_address__iendswith':domain.filter}
                    q = q | Q(**kw)
                listing = listing.filter(q)
            else:
                listing = listing.filter(to_address__iendswith='example.net')
        if user_type == 'U':
            if addresses:
                for email in addresses:
                   load_email.append(email.filter)
                   kw = {'to_address__exact':email.filter}
                   q = q | Q(**kw)
                load_email.append(request.user.username)
                kw = {'to_address__exact':request.user.username}
                q = q | Q(**kw)
                listing = listing.filter(q)
            else:
                load_email.append(request.user.username)
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
            'ld':load_domain,'user_type':user_type,'le':load_email})

@login_required
def add_to_list(request):
    template = 'lists/add.html'
    load_domain = []
    load_email = []
    user_type = 'A'
    error_msg = ''
    if not request.user.is_superuser:
        user_type = request.session['user_filter']['user_type']
        addresses = request.session['user_filter']['filter_addresses']
        q = Q()
        if user_type == 'D':
            if addresses:
                for domain in addresses:
                    load_domain.append(domain.filter)
        if user_type == 'U':
            if addresses:
                for email in addresses:
                    load_email.append(email.filter)
            else:
                load_email.append(request.user.username)

    if request.method == 'GET':
        if user_type == 'U':
            add_form = UserListAddForm(request.POST)
        else:
            add_form = ListAddForm() 
        add_dict = {'form':add_form,'user':request.user,'ld':load_domain,'user_type':user_type,'le':load_email}
    elif request.method == 'POST':
        user_type = request.session['user_filter']['user_type']
        if user_type == 'U':
            form = UserListAddForm(request.POST)
        else:
            form = ListAddForm(request.POST) 
        if form.is_valid():
            clean_data = form.cleaned_data
            if user_type != 'U':
                if clean_data['to_domain'] != '' and clean_data['to_address'] != 'default':
                    to = "%s@%s" % (clean_data['to_address'],clean_data['to_domain'])
                elif clean_data['to_domain'] != '' and clean_data['to_address'] == 'default':
                    to = clean_data['to_domain']
                else:
                    to = clean_data['to_address']
            else:
                to = clean_data['to_address']
            if not request.user.is_superuser:
                addresses = request.session['user_filter']['filter_addresses']
                a = [address.filter for address in addresses]
                if user_type == 'D':
                    if clean_data['to_domain'] not in a:
                        error_msg = 'You do not have authorization to add filters to the %s domain' % clean_data['to_domain']
                if user_type == 'U':
                    if to != request.user.username:
                        if to not in a:
                            error_msg = 'You are only authorized to add filters to your email address %s' % request.user.username
            kwargs = {'to_address':to,'from_address':clean_data['from_address']}
            if int(clean_data['list_type']) == 1:
                try:
                    b = Blacklist.objects.get(**kwargs)
                except Blacklist.DoesNotExist:
                    wl = Whitelist(to_address=to,from_address=clean_data['from_address'])
                    if error_msg == '':
                        try:
                            wl.save()
                        except IntegrityError:
                            error_msg = 'The list item already exists'
                else:
                    error_msg = '%s is blacklisted, please remove from blacklist before attempting to whitelist' % clean_data['from_address']
            else:
                try:
                    w = Whitelist.objects.get(**kwargs)
                except Whitelist.DoesNotExist:    
                    bl = Blacklist(to_address=to,from_address=clean_data['from_address'])
                    if error_msg == '':
                        try:
                            bl.save()
                        except IntegrityError:
                            error_msg = 'The list item already exists'
                else:
                    error_msg = '%s is whitelisted, please remove from whitelist before attempting to blacklist' % clean_data['from_address']
            if request.is_ajax():
                if error_msg == '':
                    request.method = 'GET'
                    return index(request,int(clean_data['list_type']),1,'dsc','id','',3)
                else:
                    json = simplejson.dumps({'items':[],'paginator':[],'error':error_msg})
                    return HttpResponse(json,mimetype='application/javascript')
            else:
                return HttpResponseRedirect('/lists/')
        else:
            if request.is_ajax():
                error_list = form.errors.values()[0]
                html = errorlist(error_list).as_ul()
                response = simplejson.dumps({'error': html})
                return HttpResponse(response,mimetype='application/javascript')
            add_dict = {'form':form,'user':request.user,'ld':load_domain,'user_type':user_type,'le':load_email}
    return render_to_response(template,add_dict)

@never_cache
@login_required
def delete_from_list(request, list_kind, item_id):
    item_id = int(item_id)
    list_kind = int(list_kind)
    error_msg = ''
    if list_kind == 1:
        try:
            w = Whitelist.objects.get(pk=item_id)
        except Whitelist.DoesNotExist:
            if request.is_ajax():
                error_msg = 'The list item does not exist'
                pass
            else:
                raise Http404()
        else:
            if w.from_address == '127.0.0.1' and w.to_address == 'default':
                error_msg = 'This is a buildin item, it cannot be deleted'
            if not request.user.is_superuser:
                user_type = request.session['user_filter']['user_type']
                addresses = request.session['user_filter']['filter_addresses']
                a = [address.filter for address in addresses]
                if user_type == 'D':
                    dom = w.to_address
                    if '@' in dom:
                        dom = dom.split('@')[1]
                    if dom not in a:
                        error_msg = 'The list item does not belong to you'
                if user_type == 'U':
                    if request.user.username != w.to_address:
                        if w.to_address not in a:
                            error_msg = 'The list item does not belong to you'
            if error_msg == '':
                w.delete()
    elif list_kind == 2:
        try:
            b = Blacklist.objects.get(pk=item_id)
        except Blacklist.DoesNotExist:
            if request.is_ajax():
                error_msg = 'The list item does not exist'
                pass
            else:
                raise Http404()
        else:
            if not request.user.is_superuser:
                user_type = request.session['user_filter']['user_type']
                addresses = request.session['user_filter']['filter_addresses']
                a = [address.filter.filter for address in addresses]
                if user_type == 'D':
                    dom = b.to_address
                    if '@' in dom:
                        dom = dom.split('@')[1]
                    if dom not in a:
                        error_msg = 'The list item does not belong to you'
                if user_type == 'U':
                    if request.user.username != b.to_address:
                        if b.to_address not in a:
                            error_msg = 'The list item does not belong to you'
            if error_msg == '':
                b.delete()
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
            return index(request,list_kind,page,direction,order_by,'',3)
        else:
            json = simplejson.dumps({'items':[],'paginator':[],'error':error_msg})
            return HttpResponse(json,mimetype='application/javascript')
    else:
        return HttpResponseRedirect('/lists/')

