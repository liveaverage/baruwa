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
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from baruwa.utils.decorators import onlysuperusers
from baruwa.accounts.models import UserAddresses
from baruwa.config.models import MailHost
from baruwa.config.forms import  MailHostForm, EditMailHost, DeleteMailHost, \
InitializeConfigsForm
from baruwa.utils.misc import jsonify_domains_list
from baruwa.config.models import MailAuthHost, ScannerHost, ScannerConfig, \
ConfigSection
from baruwa.config.forms import MailAuthHostForm, EditMailAuthHostForm, \
 DeleteMailAuthHostForm


AUTH_TYPES = ['', 'pop3', 'imap', 'smtp']

@login_required
@onlysuperusers
def index(request, page=1, direction='dsc', order_by='id', 
        template='config/index.html'):
    """
    Displays a paginated list of domains mail is processed for
    """
    if request.user.is_superuser:
        domains = UserAddresses.objects.values(
        'id', 'enabled', 'address', 'user__id', 'user__username', 
        'user__first_name', 'user__last_name').filter(address_type=1)
    else:
        domains = UserAddresses.objects.values(
        'id', 'enabled', 'address', 'user__id', 'user__username', 
        'user__first_name', 'user__last_name').filter(
        address_type=1).filter(user=request.user)
        
    if request.is_ajax():
        p = Paginator(domains, 15)
        if page == 'last':
            page = p.num_pages
        po = p.page(page)
        domains = map(jsonify_domains_list, po.object_list)
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
        'app': 'settings', 'list_all':1, 'direction':direction, 
        'order_by':order_by}
        json = simplejson.dumps({'items':domains, 'paginator':pg})
        return HttpResponse(json, mimetype='application/javascript')    
    return  object_list(request, template_name=template, queryset=domains, 
        paginate_by=15, page=page, extra_context={'app':'settings', 
        'direction':direction, 'order_by':order_by, 'list_all':1})
    
@login_required
@onlysuperusers    
def view_domain(request, domain_id, template='config/domain.html'):
    "Displays a domain"
    
    domain = get_object_or_404(UserAddresses, id=domain_id, 
        address_type=1)
    
    servers = MailHost.objects.filter(useraddress=domain)
    authservers = MailAuthHost.objects.filter(useraddress=domain)
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))

@login_required
@onlysuperusers    
def add_host(request, domain_id, template='config/add_host.html'):
    "Adds Mail host"
    
    domain = get_object_or_404(UserAddresses, id=domain_id, address_type=1)
    
    if request.method == 'POST':
        form = MailHostForm(request.POST)
        if form.is_valid():
            try:
                host = form.save()
                msg = _('Delivery SMTP server: %(server)s was'
                        ' added successfully') % {'server':host.address}
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', 
                    args=[domain.id]))
            except:
                msg = _('Adding of Delivery SMTP server failed')
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
    else:
        form =  MailHostForm(initial = {'useraddress': domain.id})
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))
    
@login_required
@onlysuperusers
def edit_host(request, host_id, template='config/edit_host.html'):
    "Edists Mail host"
    
    host = get_object_or_404(MailHost, id=host_id)
    
    if request.method == 'POST':
        form = EditMailHost(request.POST, instance=host)
        if form.is_valid():
            try:
                form.save()
                msg = _('Delivery SMTP server: %(server)s has '
                        'been updated successfully') % {'server':host.address}
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', 
                    args=[host.useraddress.id]))
            except:
                msg = _('Delivery SMTP server: %(server)s update failed') % {
                'server':host.address}
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
    else:
        form = EditMailHost(instance=host)
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))
    
@login_required
@onlysuperusers
def delete_host(request, host_id, template='config/delete_host.html'):
    'Deletes Mail host'
    
    host = get_object_or_404(MailHost, id=host_id)
    
    if request.method == 'POST':
        form = DeleteMailHost(request.POST, instance=host)
        if form.is_valid():
            try:
                go_id = host.useraddress.id
                msg = _('Delivery SMTP server: %(server)s has been deleted') % {
                'server':host.address}
                host.delete()
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', 
                                            args=[go_id]))
            except:
                msg = _('Delivery SMTP server: %(server)s could not be deleted') % {
                'server':host.address}
                if request.is_ajax():
                    response = simplejson.dumps({'success':False, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
    else:
        form = DeleteMailHost(instance=host)
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))
    
@login_required
@onlysuperusers
def test_host(request, host_id):
    'Tests SMTP delivery to mail host'
    
    host = get_object_or_404(MailHost, id=host_id)
    
    test_address = "postmaster@%s" % host.useraddress.address
    from baruwa.utils.process_mail import test_smtp_server
    
    if test_smtp_server(host.address, host.port, test_address):
        msg = _('Server %(server)s is operational and'
                ' accepting mail for: %(dom)s') % {
                'server':host.address, 
                'dom':host.useraddress.address}
        success = True
    else:
        success = False
        msg = _('Server %(server)s is NOT accepting mail for : %(dom)s') % {
        'server':host.address, 'dom':host.useraddress.address}
        
    if request.is_ajax():
        response = simplejson.dumps({'success':success, 'html':msg})
        return HttpResponse(response, 
            content_type='application/javascript; charset=utf-8')
        
    request.user.message_set.create(message=msg)
    return HttpResponseRedirect(reverse('view-domain', 
        args=[host.useraddress.id]))
    
@login_required
@onlysuperusers
def add_auth_host(request, domain_id, template='config/add_auth_host.html'):
    'Add an external auth host'
    domain = get_object_or_404(UserAddresses, id=domain_id, address_type=1)
    if request.method == 'POST':
        form = MailAuthHostForm(request.POST)
        if form.is_valid():
            try:
                host = form.save()
                msg = _('External authentication %(auth)s: on host %(host)s'
                        ' for domain %(dom)s was added successfully') % {
                    'auth':AUTH_TYPES[host.protocol], 'host':host.address, 
                    'dom':host.useraddress.address}
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', 
                    args=[domain.id]))
            except:
                msg = _('Addition of external authentication failed')
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
    else:
        form = MailAuthHostForm(initial = {'useraddress': domain.id})
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))

@login_required
@onlysuperusers
def edit_auth_host(request, host_id, template='config/edit_auth_host.html'):
    'Edits an external auth host'
    
    host = get_object_or_404(MailAuthHost, id=host_id)
    
    if request.method == 'POST':
        form = EditMailAuthHostForm(request.POST, instance=host)
        if form.is_valid():
            try:
                saved_host = form.save()
                msg = _('External authentication %(auth)s: on host %(host)s for'
                        ' domain %(dom)s has been updated successfully') % {
                    'auth':AUTH_TYPES[saved_host.protocol], 
                    'host':saved_host.address, 
                    'dom':saved_host.useraddress.address}
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', 
                    args=[saved_host.useraddress.id]))
            except:
                msg = _('Update of external authentication failed')
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
    else:
        form = EditMailAuthHostForm(instance=host)
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))

@login_required
@onlysuperusers
def delete_auth_host(request, host_id, 
                    template='config/delete_auth_host.html'):
    'Deletes an external auth host'
    host = get_object_or_404(MailAuthHost, id=host_id)
    
    if request.method == 'POST':
        form = DeleteMailAuthHostForm(request.POST, instance=host)
        if form.is_valid():
            try:
                go_id = host.useraddress.id
                msg = _('External authentication %(auth)s: on host %(host)s'
                        ' for domain %(dom)s has been deleted') % {
                            'auth':AUTH_TYPES[host.protocol], 
                            'host':host.address, 
                            'dom':host.useraddress.address
                        }
                host.delete()
                if request.is_ajax():
                    response = simplejson.dumps({'success':True, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', args=[go_id]))
            except:
                msg = _('External authentication %(auth)s: on host %(host)s'
                        ' for domain %(dom)s could not be deleted') % {
                        'auth':AUTH_TYPES[host.protocol], 
                        'host':host.address, 
                        'dom':host.useraddress.address
                        }
                if request.is_ajax():
                    response = simplejson.dumps({'success':False, 'html':msg})
                    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
                request.user.message_set.create(message=msg)
    else:
        form = DeleteMailAuthHostForm(instance=host)
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))

@login_required
@onlysuperusers
def list_scanners(request, page=1, direction='dsc', order_by='id', 
                template='config/list_scanners.html'):
    'lists the scanning nodes'
    scanners = ScannerHost.objects.values('id', 'address')
    configs = ScannerConfig.objects.values('value')[:1]
    
    if request.is_ajax():
        p = Paginator(scanners, 15)
        if page == 'last':
            page = p.num_pages
        po = p.page(page)
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
        'app': 'settings', 'list_all':1, 'direction':direction, 
        'order_by':order_by}
        json = simplejson.dumps({'items':scanners, 'paginator':pg})
        return HttpResponse(json, mimetype='application/javascript')    
    return  object_list(request, template_name=template, queryset=scanners, 
        paginate_by=15, page=page, extra_context={'app':'settings', 
        'direction':direction, 'order_by':order_by, 'list_all':1})
        
@login_required
@onlysuperusers
def view_scanner(request, scanner_id, template='config/view_scanner.html'):
    'Displays links to various scanner configuration sections'
    scanner = get_object_or_404(ScannerHost, id=scanner_id)
    configs = ScannerConfig.objects.values('value')
    if not configs:
        msg = _('The node %(node)s is not been initialized,'
                ' Please initialize') % {'node':scanner.address}
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse('init-scanner', 
                                    args=[scanner.id]))

    sections = ConfigSection.objects.values('id', 'name')
    side1 = sections[:14]
    side2 = sections[14:]
    
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))
    
@login_required
@onlysuperusers
def init_scanner(request, scanner_id, template='config/init_scanner.html'):
    'Initialiazes the default scanner configuration values'
    scanner = get_object_or_404(ScannerHost, id=scanner_id)
    if request.method == 'POST':
        form = InitializeConfigsForm(request.POST)
        if form.is_valid():
            try:
                from django.conf import settings
                from django.db import connection
                import re
                path = getattr(
                settings,'TEMPLATE_DIRS', ('/tmp'))[0] + '/config/scanner-init.sql'
                sql_file = open(path, 'r')
                sql = sql_file.read()
                sql_file.close()
                sql = re.sub(r'scanner_id', str(scanner.id), sql)
                conn = connection.cursor()
                conn.execute(sql)
                msg = _('The node %(node)s has been initialized') % {'node':scanner.address}
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-scanner', 
                                            args=[scanner.id]))
            except:
                msg = 'Initialization of node %s failed' % scanner.address
                request.user.message_set.create(message=msg)          
    else:
        form = InitializeConfigsForm(initial = {'id': scanner.id})
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))

@login_required
@onlysuperusers
def view_settings(request, scanner_id, section_id, 
                template='config/view_settings.html'):
    'Displays settings on a section basis'
    return render_to_response(template, locals(), 
        context_instance=RequestContext(request))
   