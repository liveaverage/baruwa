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

import os

from subprocess import Popen, PIPE

from django.conf import settings
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import DatabaseError
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required

from baruwa.utils.decorators import onlysuperusers
from baruwa.web.config.models import Time, Source, DestinationComponent
from baruwa.web.config.models import Destination, OrderedDestination
from baruwa.web.config.models import DestinationPolicy, AclRule
from baruwa.web.config.forms import TimeForm, SourceForm, DestForm, DCForm
from baruwa.web.config.forms import DPSForm, ACLForm, ApplyForm
from baruwa.web.config.utils import lock_tables, unlock_tables


@login_required
@onlysuperusers
def index(request):
    "Index links"
    return render_to_response('web/config/index.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def acls(request, page=1):
    "ACL Rules"
    template_name = 'web/config/acls.html'

    acls = AclRule.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=acls, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/acls'},
    allow_empty=True)


@login_required
@onlysuperusers
def add_acl(request):
    "add an acl"
    if request.method == 'POST':
        form = ACLForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = _('The ACL rule was created successfully')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('acl-rules'))
            except DatabaseError, e:
                print e
                msg = _('The ACL rule could not be created')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('acl-rules'))
    else:
        form = ACLForm()
    #form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/add_acl.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def edit_acl(request, aclid):
    "Edit an acl"
    acl = get_object_or_404(AclRule, pk=aclid)
    if request.method == 'POST':
        form = ACLForm(request.POST, instance=acl)
        if form.is_valid():
            try:
                form.save()
                msg = _('The ACL Rule has been updated')
            except DatabaseError:
                msg = _('The ACL Rule could not be updated')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('acl-rules'))
    else:
        form = ACLForm(instance=acl)
    return render_to_response('web/config/edit_acl.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def delete_acl(request, aclid):
    "Delete a time period"
    acl = get_object_or_404(AclRule, pk=aclid)
    if request.method == 'POST':
        form = ACLForm(request.POST, instance=acl)
        if form.is_valid():
            try:
                acl.delete()
                msg = _('The ACL Rule has been deleted')
            except DatabaseError:
                msg = _('The ACL Rule could not be deleted')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('acl-rules'))
    else:
        form = ACLForm(instance=acl)
    return render_to_response('web/config/delete_acl.html', locals(),
        context_instance=RequestContext(request))

@login_required
@onlysuperusers
def move_acl(request, aclid, direction):
    "Delete a time period"
    acl = get_object_or_404(AclRule, pk=aclid)
    if direction == 'up':
        acl.move_up()
    else:
        acl.move_down()
    if '/settings/acls/' in request.META['HTTP_REFERER']:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect(reverse('acl-rules'))


@login_required
@onlysuperusers
def times(request, page=1):
    "Time periods"
    template_name = 'web/config/times.html'

    time_list = Time.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=time_list, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/times'},
    allow_empty=True)


@login_required
@onlysuperusers
def add_time(request):
    "add a time period"
    if request.method == 'POST':
        form = TimeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = _('The time period was created successfully')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('time-rules'))
            except DatabaseError:
                msg = _('The time period could not be created')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('time-rules'))
    else:
        form = TimeForm()
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/add_time.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def edit_time(request, tid):
    "Edit a time period"
    time_period = get_object_or_404(Time, pk=tid)
    if request.method == 'POST':
        form = TimeForm(request.POST, instance=time_period)
        if form.is_valid():
            try:
                form.save()
                msg = _('The time period has been updated')
            except DatabaseError:
                msg = _('The time period could not be updated')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('time-rules'))
    else:
        form = TimeForm(instance=time_period)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/edit_time.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def delete_time(request, tid):
    "Delete a time period"
    time_period = get_object_or_404(Time, pk=tid)
    if request.method == 'POST':
        form = TimeForm(request.POST, instance=time_period)
        if form.is_valid():
            try:
                time_period.delete()
                msg = _('The time period has been deleted')
            except DatabaseError:
                msg = _('The time period could not be deleted')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('time-rules'))
    else:
        form = TimeForm(instance=time_period)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/delete_time.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def sources(request, page=1):
    "Sources"
    template_name = 'web/config/sources.html'

    time_list = Source.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=time_list, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/sources'},
    allow_empty=True)


@login_required
@onlysuperusers
def add_source(request):
    "add a source"
    if request.method == 'POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = _('The source was created successfully')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('source-rules'))
            except DatabaseError:
                msg = _('The source could not be created')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('source-rules'))
    else:
        form = SourceForm()
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/add_source.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def edit_source(request, sid):
    "Edit a source"
    source = get_object_or_404(Source, pk=sid)
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            try:
                form.save()
                msg = _('The source has been updated')
            except DatabaseError:
                msg = _('The source could not be updated')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('source-rules'))
    else:
        form = SourceForm(instance=source)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/edit_source.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def delete_source(request, sid):
    "Delete a source"
    source = get_object_or_404(Source, pk=sid)
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            try:
                source.delete()
                msg = _('The source has been deleted')
            except DatabaseError:
                msg = _('The source could not be deleted')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('source-rules'))
    else:
        form = SourceForm(instance=source)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/delete_source.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def destination_component(request, page=1):
    "Destination components"
    template_name = 'web/config/dc.html'

    dcomp = DestinationComponent.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=dcomp, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/dcs'},
    allow_empty=True)


@login_required
@onlysuperusers
def add_dc(request):
    "add a destination component"
    if request.method == 'POST':
        form = DCForm(request.POST)
        if form.is_valid():
            try:
                model = form.save(commit=False)
                model.save()
                form.save_m2m()
                msg = _('The destination component was created successfully')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('dc-rules'))
            except DatabaseError:
                msg = _('The destination component could not be created')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('dc-rules'))
    else:
        form = DCForm()
    for name in ['url', 'domain', 'regex']:
        form.fields[name].widget.attrs['size'] = '45'
    return render_to_response('web/config/add_dc.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def edit_dc(request, dcid):
    "Edit a Destination component"
    dcomp = get_object_or_404(DestinationComponent, pk=dcid)
    if request.method == 'POST':
        form = DCForm(request.POST, instance=dcomp)
        if form.is_valid():
            try:
                model = form.save(commit=False)
                model.save()
                form.save_m2m()
                msg = _('The destination component has been updated')
            except DatabaseError:
                msg = _('The destination component could not be updated')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('dc-rules'))
    else:
        form = DCForm(instance=dcomp)
    for name in ['url', 'domain', 'regex']:
        form.fields[name].widget.attrs['size'] = '45'
    return render_to_response('web/config/edit_dc.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def delete_dc(request, dcid):
    "Delete a Destination component"
    dcomp = get_object_or_404(DestinationComponent, pk=dcid)
    if request.method == 'POST':
        form = DCForm(request.POST, instance=dcomp)
        if form.is_valid():
            try:
                dcomp.delete()
                msg = _('The destination component has been deleted')
            except DatabaseError:
                msg = _('The destination component could not be deleted')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('dc-rules'))
    else:
        form = DCForm(instance=dcomp)
    for name in ['url', 'domain', 'regex']:
        form.fields[name].widget.attrs['size'] = '45'
    return render_to_response('web/config/delete_dc.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def destinations(request, page=1):
    "Destinations"
    template_name = 'web/config/destinations.html'

    destinations = Destination.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=destinations, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/destinations'},
    allow_empty=True)


@login_required
@onlysuperusers
def add_destination(request):
    "add a destination"
    if request.method == 'POST':
        form = DestForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = _('The destination was created successfully')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('destination-rules'))
            except DatabaseError:
                msg = _('The destination could not be created')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('destination-rules'))
    else:
        form = DestForm()
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/add_destination.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def edit_destination(request, did):
    "Edit a Destination"
    dest = get_object_or_404(Destination, pk=did)
    if request.method == 'POST':
        form = DestForm(request.POST, instance=dest)
        if form.is_valid():
            try:
                form.save()
                msg = _('The destination has been updated')
            except DatabaseError:
                msg = _('The destination could not be updated')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('destination-rules'))
    else:
        form = DestForm(instance=dest)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/edit_destination.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def delete_destination(request, did):
    "Delete a Destination"
    dest = get_object_or_404(Destination, pk=did)
    if request.method == 'POST':
        form = DestForm(request.POST, instance=dest)
        if form.is_valid():
            try:
                dest.delete()
                msg = _('The destination has been deleted')
            except DatabaseError:
                msg = _('The destination could not be deleted')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('destination-rules'))
    else:
        form = DestForm(instance=dest)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/delete_destination.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def ordered_destinations(request, page=1):
    "Ordered destinations"
    template_name = 'web/config/ods.html'

    ods = OrderedDestination.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=ods, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/ods'},
    allow_empty=True)


@login_required
@onlysuperusers
def destination_policy(request, page=1):
    "Destination policies"
    template_name = 'web/config/dps.html'

    dps = DestinationPolicy.objects.all()
    
    return object_list(request, template_name=template_name,
    queryset=dps, paginate_by=10, page=page,
    extra_context={'list_all': 1, 'app': 'web/settings/dps'},
    allow_empty=True)


@login_required
@onlysuperusers
def add_dps(request):
    "add a destination policy"
    if request.method == 'POST':
        form = DPSForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = _('The destination policy was created successfully')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('dps-rules'))
            except DatabaseError:
                msg = _('The destination policy could not be created')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('dps-rules'))
    else:
        form = DPSForm()
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/add_dps.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def edit_dps(request, dpid):
    "Edit a Destination policy"
    dps = get_object_or_404(DestinationPolicy, pk=dpid)
    if request.method == 'POST':
        form = DPSForm(request.POST, instance=dps)
        if form.is_valid():
            try:
                form.save()
                msg = _('The destination policy has been updated')
            except DatabaseError:
                msg = _('The destination policy could not be updated')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('dps-rules'))
    else:
        form = DPSForm(instance=dps)
    form.fields['name'].widget.attrs['size'] = '45'
    if dps.name.isupper():
        form.fields['name'].widget.attrs['readonly'] = True
    return render_to_response('web/config/edit_dps.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def delete_dps(request, dpid):
    "Delete a Destination policy"
    dps = get_object_or_404(DestinationPolicy, pk=dpid)
    if request.method == 'POST':
        form = DPSForm(request.POST, instance=dps)
        if form.is_valid():
            try:
                dps.delete()
                msg = _('The destination policy has been deleted')
            except DatabaseError:
                msg = _('The destination policy could not be deleted')
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('dps-rules'))
    else:
        form = DPSForm(instance=dps)
    form.fields['name'].widget.attrs['size'] = '45'
    return render_to_response('web/config/delete_dps.html', locals(),
        context_instance=RequestContext(request))


@login_required
@onlysuperusers
def verify_config(request):
    "Verify configuration"
    cmd = getattr(settings, 'BARUWA_WEB_VERIFY_CMD')
    if not os.path.exists(cmd):
        msg = _('The verify command does not exist')
        messages.info(request, msg)
        return HttpResponseRedirect(reverse('acl-rules'))

    try:
        lock_tables()
        pipe = Popen([cmd], stdout=PIPE, stderr=PIPE)
        stdout, stderr = pipe.communicate()
        if pipe.returncode == 0:
            success = True
        else:
            success = False
    except OSError, exception:
        stdout += str(exception)
        success = False
    finally:
        unlock_tables()

    return render_to_response('web/config/verify.html', locals(),
        context_instance=RequestContext(request))

@login_required
@onlysuperusers
def apply_config(request):
    "Apply configuration"
    if request.method == 'POST':
        confirm = False
        form = ApplyForm(request.POST)
        if form.is_valid():
            vcmd = getattr(settings, 'BARUWA_WEB_VERIFY_CMD')
            acmd = getattr(settings, 'BARUWA_WEB_APPLY_CMD')

            if not os.path.exists(vcmd):
                msg = _('The verify command does not exist')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('acl-rules'))
            if not os.path.exists(acmd):
                msg = _('The apply command does not exist')
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('acl-rules'))

            try:
                lock_tables()
                pipe = Popen([vcmd], stdout=PIPE, stderr=PIPE)
                stdout, stderr = pipe.communicate()
                if pipe.returncode != 0:
                    raise ValueError(stdout)
                pipe = Popen([acmd], stdout=PIPE, stderr=PIPE)
                stdout, stderr = pipe.communicate()
                if pipe.returncode == 0:
                    success = True
                else:
                    success = False
            except (OSError, ValueError), exception:
                stdout += str(exception)
                success = False
            finally:
                unlock_tables()
        else:
            print form.errors
    else:
        confirm = True
        form = ApplyForm(initial={'sentry': 1})
    return render_to_response('web/config/apply.html', locals(),
        context_instance=RequestContext(request))