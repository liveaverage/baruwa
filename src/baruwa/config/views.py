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
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.urlresolvers import reverse
from baruwa.utils.decorators import onlysuperusers
from baruwa.accounts.models import UserAddresses
from baruwa.config.models import MailHost
from baruwa.config.forms import  MailHostForm, EditMailHost, DeleteMailHost

@login_required
@onlysuperusers
def index(request, page=1, template='config/index.html'):
    """
    Displays a paginated list of domains mail is processed for
    """
    if request.user.is_superuser:
        domains = UserAddresses.objects.all()
    else:
        domains = UserAddresses.objects.filter(user=request.user)
        
    return  object_list(request, template_name=template, 
        queryset=domains, paginate_by=10, page=page, extra_context={'app':'settings', 'list_all':1})
    
@login_required
@onlysuperusers    
def view_domain(request, domain_id, template='config/domain.html'):
    "Displays a domain"
    domain = get_object_or_404(UserAddresses, id=domain_id, address_type=1)
    servers = MailHost.objects.filter(useraddress=domain)
    return render_to_response(template, locals(), context_instance=RequestContext(request))

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
                msg = 'Delivery SMTP server: %s was added successfully' % host.address
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', args=[domain.id]))
            except:
                msg = 'Adding of Delivery SMTP server failed'
                request.user.message_set.create(message=msg)
    else:
        form =  MailHostForm(initial = {'useraddress': domain.id})
    return render_to_response(template, locals(), context_instance=RequestContext(request))
    
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
                msg = 'Delivery SMTP server: %s has been updated successfully' % host.address
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', args=[host.useraddress.id]))
            except:
                msg = 'Delivery SMTP server: %s update failed' % host.address
                request.user.message_set.create(message=msg)
    else:
        form = EditMailHost(instance=host)
    return render_to_response(template, locals(), context_instance=RequestContext(request))
    
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
                msg = 'Delivery SMTP server: %s has been deleted' % host.address
                host.delete()
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(reverse('view-domain', args=[go_id]))
            except:
                msg = 'Delivery SMTP server: %s could not be deleted' % host.address
                request.user.message_set.create(message=msg)
    else:
        form = DeleteMailHost(instance=host)
    return render_to_response(template, locals(), context_instance=RequestContext(request))
    
@login_required
@onlysuperusers
def test_host(request, host_id):
    'Tests SMTP delivery to mail host'
    host = get_object_or_404(MailHost, id=host_id)
    test_address = "postmaster@%s" % host.useraddress.address
    from baruwa.utils.process_mail import test_smtp_server
    if test_smtp_server(host.address, host.port, test_address):
        msg = 'Server %s is operational and accepting mail for: %s' % (host.address, host.useraddress.address)
        request.user.message_set.create(message=msg)
    else:
        msg = 'Server %s is NOT accepting mail for : %s' % (host.address, host.useraddress.address)
        request.user.message_set.create(message=msg)
    return HttpResponseRedirect(reverse('view-domain', args=[host.useraddress.id]))
    