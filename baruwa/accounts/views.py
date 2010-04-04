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
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponseBadRequest,HttpResponse
from django.forms.util import ErrorList as errorlist
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from baruwa.accounts.models import Users,UserFilters
from baruwa.accounts.forms import UserForm,StrippedUserForm,UserFilterForm,DomainUserFilterForm
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
    Displays user accounts.
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
        except:
            error_msg = 'Account creation failed'
        else:
            if new_user.password != 'XXXXXXXXXX':
                m = md5.new(new_user.password)
                hashv = m.hexdigest()
                new_user.password = hashv
                form = UserForm()
                new_user.save()
            else:
                error_msg = 'Please provide a password'
    else:
        form = UserForm()
    user_list = Users.objects.all()
    return object_list(request,template_name='accounts/index.html',queryset=user_list,paginate_by=10,page=page,
        extra_context={'quarantine':0,'direction':direction,'order_by':ordering,'app':'accounts','active_filters':[],'list_all':1,'form':form})

@never_cache
@login_required
def user_account(request,user_name=None,add_filter=False):
    """
    Displays user account info.
    """
    if not request.user.is_superuser and add_filter:
        return HttpResponseRedirect(reverse('user-profile',args=[request.user.username]))

    if not request.user.is_superuser:
        login = Users.objects.get(pk=request.user.username)
        if login:
            if login.type == 'D':
                if login.username != user_name:
                    addresses = request.session['user_filter']['filter_addresses']
                    d = [domain.filter for domain in addresses]
                    try:
                        ld = user_name.split('@')[1]
                    except:
                        ld = 'example.net'
                    if ld not in d:
                        response = HttpResponseForbidden('Hahaha - play nice, dont try access profiles in domains you do not manage')
                        return response
            if login.type == 'U':
                if login.username != user_name:
                    response = HttpResponseForbidden('Hahaha - play nice, dont try access other users profiles')
                    return response
        else:
            response = HttpResponseBadRequest('Error occured why processing your session info')
            return response
    user_object = Users.objects.get(pk=user_name) #get_object_or_404(Users,pk=user_name)
    user_filters = UserFilters.objects.values('filter','active').filter(username__exact=user_name)
    if request.method == 'POST':
        if request.user.is_superuser:
            form = UserForm(request.POST,instance=user_object)
        else:
            form = StrippedUserForm(request.POST,instance=user_object)
        try:
            updated_user_object = form.save(commit=False)
        except:
            error_msg = 'The account could not be updated'
        else:
            if updated_user_object.password != 'XXXXXXXXXX':
                m = md5.new(updated_user_object.password)
                hashv = m.hexdigest()
                updated_user_object.password = hashv
            else:
                user_object = get_object_or_404(Users,pk=user_name)
                updated_user_object.password = user_object.password
            updated_user_object.save()
            user_object = get_object_or_404(Users,pk=user_name)
            if request.user.is_superuser:
                form = UserForm(instance=user_object)
            else:
                form = StrippedUserForm(instance=user_object)
    else:
        if request.user.is_superuser and add_filter:
            form = UserFilterForm()
        else:
            if request.user.is_superuser:
                form = UserForm(instance=user_object)
            else:
                form = StrippedUserForm(instance=user_object)
    return render_to_response('accounts/user.html',{'user':request.user,'form':form,
        'filters':user_filters,'target_user':user_name,'add_filter':add_filter})

# modified from django source
def login(request,redirect_field_name=REDIRECT_FIELD_NAME):
    "Displays the login form and handles the login action."
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

def add_filter(request,user_name):
    "Adds a filter to a user account"
    if request.user.is_superuser:
        if request.method == "POST":
            user_object = Users.objects.get(pk=user_name)
            if user_object.type == 'D':
                form = DomainUserFilterForm(request.POST)
            elif user_object.type == 'U':
                form = UserFilterForm(request.POST)
            if form.is_valid():
                u = UserFilters(username=form.cleaned_data['username'],filter=form.cleaned_data['filter'],active=form.cleaned_data['active'])
                u.save()
                if request.is_ajax():
                    response = simplejson.dumps({'success':'True','html':'Filter has been created',
                        'data':[form.cleaned_data['filter'],form.cleaned_data['active'],form.cleaned_data['username']]})
                    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
                else:
                    return HttpResponseRedirect(reverse('user-profile',args=[user_name]))
            else:
                if request.is_ajax():
                    error_list = form.errors.values()[0][0]
                    #html = errorlist(error_list).as_ul()
                    html = "Error occured : %s" % error_list
                    response = simplejson.dumps({'success':'False','html':html,'data':[]})
                    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
                else:
                    return HttpResponseRedirect(reverse('add-filter',args=[user_name]))
        else:
            return HttpResponseRedirect(reverse('add-filter',args=[user_name]))
    else:
        return HttpResponseRedirect(reverse('user-profile',args=[user_name]))

def delete_filter(request,user_name,filter):
    "Deletes a filter"
    if request.user.is_superuser:
        error_msg = ''
        try:
            filter = UserFilters.objects.get(username=user_name,filter=filter)
        except:
            pass
        try:
            filter.delete()
        except:
            error_msg = 'Deletion of filter failed'
        if request.is_ajax():
            if error_msg == '':
                response = simplejson.dumps({'success':'True','html':'Filter has been deleted'})
            else:
                response = simplejson.dumps({'success':'False','html':'Deletion of the filter failed'})
            return HttpResponse(response, content_type='application/javascript; charset=utf-8')
        else:
            return HttpResponseRedirect(reverse('user-profile',args=[user_name]))
    else:
        return HttpResponseRedirect(reverse('user-profile',args=[request.user.username]))
