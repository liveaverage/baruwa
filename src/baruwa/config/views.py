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
from django.shortcuts import render_to_response
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from baruwa.utils.decorators import onlysuperusers
from baruwa.accounts.models import UserAddresses

@login_required
@onlysuperusers
def index(request, page=1, template='config/index.html'):
    """index"""
    if request.user.is_superuser:
        domains = UserAddresses.objects.all()
    else:
        domains = UserAddresses.objects.filter(user=request.user)
        
    return  object_list(request, template_name=template, 
        queryset=domains, paginate_by=10, page=page, extra_context={'app':'settings', 'list_all':1})
    #
    
def view_domain(request, template='config/domain.html'):
    ""
    return render_to_response(template, locals(), context_instance=RequestContext(request))