from django.core.exceptions import PermissionDenied

def onlysuperusers(function):
    """
    """
    def _inner(request,*args,**kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request,*args,**kwargs)
    return _inner
