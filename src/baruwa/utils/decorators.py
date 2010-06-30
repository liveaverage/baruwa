from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

def onlysuperusers(function):
    """
    """
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request,*args,**kwargs)
    return _inner
    
def authorized_users_only(function):
    """
    This checks if a user is allowed access to a 
    user account
    """
    
    def _inner(request, *args, **kwargs):
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
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            if account_type != 2:
                raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner