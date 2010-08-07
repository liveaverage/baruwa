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

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

def onlysuperusers(function):
    """
    Allow access only to super users
    """
    def _inner(request, *args, **kwargs):
        "check if is super user"
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner
    
def authorized_users_only(function):
    """
    This checks if a user is allowed access to a 
    user account
    """
    
    def _inner(request, *args, **kwargs):
        "check if super user"
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            user_id = kwargs['user_id']
            account_info = get_object_or_404(User, pk=user_id)
            if account_type == 2:
                if request.user.id != account_info.id:
                    domains = request.session['user_filter']['addresses']
                    if '@' in account_info.username:
                        dom = account_info.username.split('@')[1]
                        if not dom in domains:
                            raise PermissionDenied
                    else:
                        raise PermissionDenied
            elif account_type == 3:
                if request.user.id != account_info.id:
                    raise PermissionDenied
            else:
                raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner

def only_admins(function):
    """
    Allows view access for only admins and domain admins
    """
    def _inner(request, *args, **kwargs):
        "check if authorized admin"
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            if account_type != 2:
                raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner