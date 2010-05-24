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
from django.shortcuts import render_to_response,get_object_or_404
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.forms.util import ErrorList as errorlist
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from baruwa.accounts.models import User, UserFilters
from baruwa.accounts.forms import UserForm, UserUpdateForm, StrippedUserForm, UserFilterForm, DomainUserFilterForm, DeleteFilter
from baruwa.reports.views import set_user_filter
from baruwa.utilities.decorators import onlysuperusers
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
try:
    import hashlib as md5
except ImportError:
    import md5

@never_cache
@login_required
@onlysuperusers
def index(request,page=1,direction='dsc',order_by='username'):
    """
    Displays user accounts and creates user accounts.
    """
    error_msg = ''
    ordering = order_by
    if direction == 'dsc':
        ordering = order_by
        order_by = "-%s" % order_by
    if request.method == 'POST':
        form = UserForm(request.POST)
        try:
            new_user = form.save(commit=False)
            m = md5.new(new_user.password)
            hashv = m.hexdigest()
            new_user.password = hashv
            new_user.save()
        except:
            error_msg = 'Account creation failed'
        if request.is_ajax():
            if error_msg == '':
                response = simplejson.dumps({'error':'','form_field':''})
            else:
                if form.errors.values():
                    error_list = form.errors.values()[0]
                    html = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
                else:
                    error_list = [error_msg]
                    html = {'none':['none']}
                response = simplejson.dumps({'error': unicode(error_list[0]),'form_field':html.keys()[0]})
            return HttpResponse(response,mimetype='application/javascript')
        #form = UserForm()
    else:
        form = UserForm()
    form.fields['spamscore'].widget.attrs['size'] = '4'
    form.fields['highspamscore'].widget.attrs['size'] = '4'
    user_list = User.objects.all()
    return object_list(request,template_name='accounts/index.html',queryset=user_list,paginate_by=10,page=page,
        extra_context={'quarantine':0,'direction':direction,'order_by':ordering,'app':'accounts','active_filters':[],'list_all':1,'form':form})

@never_cache
@login_required
def user_account(request, user_id=None, add_filter=False):
    """
    Displays user account info.
    """
    if not request.user.is_superuser and add_filter:
        return HttpResponseRedirect(reverse('user-profile',args=[request.user.username]))

    if user_id is None:
        user = User.objects.get(username=request.user.username)
        user_id = user.id
    else:
        user_id = int(user_id)
    try:
        vu = User.objects.get(pk=user_id)
    except:
        return HttpResponseBadRequest('Error occured')

    if not request.user.is_superuser:
        login = User.objects.get(username=request.user.username)
        if login:
            if login.type == 'D':
                if login.id != user_id:
                    addresses = request.session['user_filter']['filter_addresses']
                    d = [domain.filter for domain in addresses]
                    try:
                        ld = vu.username.split('@')[1]
                    except:
                        ld = 'example.net'
                    if ld not in d:
                        return HttpResponseForbidden('You are not authorized to access this page')
            if login.type == 'U':
                if login.username != vu.username:
                    return HttpResponseForbidden('You are not authorized to access this page')
        else:
            return HttpResponseBadRequest('Error occured why processing your session info')
    user_object = User.objects.get(pk=user_id) #get_object_or_404(User,pk=user_name)
    user_filters = UserFilters.objects.filter(username__exact=vu.username)
    if request.method == 'POST':
        if request.user.is_superuser:
            form = UserUpdateForm(request.POST,instance=user_object)
        else:
            form = StrippedUserForm(request.POST,instance=user_object)
        try:
            updated_user_object = form.save(commit=False)
            if updated_user_object.password != 'XXXXXXXXXX' and user_object.password != '':
                m = md5.new(updated_user_object.password)
                hashv = m.hexdigest()
                updated_user_object.password = hashv
            else:
                user_object = get_object_or_404(User,pk=user_id)
                updated_user_object.password = user_object.password
            updated_user_object.save()
            user_object = get_object_or_404(User,pk=user_id)
            if request.user.is_superuser:
                form = UserUpdateForm(instance=user_object)
            else:
                form = StrippedUserForm(instance=user_object)
        except:
            error_msg = 'The account could not be updated'
            if request.is_ajax():
                if form.errors.values():
                    error_list = form.errors.values()[0]
                    html = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
                else:
                    error_list = [error_msg]
                    html = {'none':['none']}
                response = simplejson.dumps({'error':unicode(error_list[0]), 'form_field':html.keys()[0]})
                return HttpResponse(response,mimetype='application/javascript')
        else:
            if request.is_ajax():
                response = simplejson.dumps({'error':'', 'form_field':''})
                return HttpResponse(response,mimetype='application/javascript')
    else:
        if request.user.is_superuser and add_filter:
            form = UserFilterForm()
        else:
            if request.user.is_superuser:
                form = UserUpdateForm(instance=user_object)
            else:
                form = StrippedUserForm(instance=user_object)
    if user_object.password == '':
        extern_user = True
    else:
        extern_user = False
    form.fields['spamscore'].widget.attrs['size'] = '4'
    form.fields['highspamscore'].widget.attrs['size'] = '4'
    return render_to_response('accounts/user.html',{'form':form,
        'filters':user_filters,'target_user':user_id,'add_filter':add_filter,
        'auth_type':extern_user,'user_name':vu.username},context_instance=RequestContext(request))

# modified from django source
@never_cache
def login(request,redirect_field_name=REDIRECT_FIELD_NAME):
    "Displays the login form and handles the login action."
    from django.conf import settings
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            set_user_filter(form.get_user(),request)
            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm(request)
    request.session.set_test_cookie()
    return render_to_response('accounts/login.html', {
        'form': form,
        redirect_field_name: redirect_to,
    }, context_instance=RequestContext(request))

@never_cache
@onlysuperusers
@login_required
def add_filter(request, user_id):
    "Adds a filter to a user account"
    if request.user.is_superuser:
        if request.method == "POST":
            user_object = User.objects.get(pk=user_id)
            if user_object.type == 'D':
                form = DomainUserFilterForm(request.POST)
            elif user_object.type == 'U':
                form = UserFilterForm(request.POST)
            if form.is_valid():
                u = UserFilters(username=user_object.username, filter=form.cleaned_data['filter'], active=form.cleaned_data['active'])
                u.save()
                u = UserFilters.objects.get(username=user_object.username, filter=form.cleaned_data['filter'], active=form.cleaned_data['active'])
                if request.is_ajax():
                    response = simplejson.dumps({'success':'True','html':'Filter has been created',
                        'data':[form.cleaned_data['filter'], form.cleaned_data['active'], form.cleaned_data['username'], u.id]})
                    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
                return HttpResponseRedirect(reverse('user-profile',args=[user_id]))
            else:
                if request.is_ajax():
                    error_list = form.errors.values()[0]
                    html = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
                    response = simplejson.dumps({'success':'False', 'html':unicode(error_list[0]), 'data':[], 'form_field':html.keys()[0]})
                    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
                return HttpResponseRedirect(reverse('add-filter',args=[user_id]))
        return HttpResponseRedirect(reverse('add-filter',args=[user_id]))

@never_cache
@onlysuperusers
@login_required
def delete_filter(request, user_id=None, filter=None):
    "Deletes a filter"
    if request.method == 'POST':
        form = DeleteFilter(request.POST)
        if form.is_valid():
            filter_id = int(form.cleaned_data['id'])
            user_id = form.cleaned_data['user_id']
            filter = get_object_or_404(UserFilters, id=filter_id)
            try:
                filter.delete()
            except:
                if request.is_ajax():
                    response = simplejson.dumps({'success':'False','html':'Deletion of the filter failed'})
                    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
            else:
                if request.is_ajax():
                    response = simplejson.dumps({'success':'True','html':'Filter has been deleted'})
                    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
            return HttpResponseRedirect(reverse('user-profile',args=[user_id]))
    else:
        form = DeleteFilter()
        form.fields['id'].widget.attrs['value'] = filter
        form.fields['user_id'].widget.attrs['value'] = user_id
        filter = get_object_or_404(UserFilters, id=filter)
    return render_to_response('accounts/delete_filter.html', {'form':form, 'item':filter}, context_instance=RequestContext(request))
