from django.shortcuts import render_to_response
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

@never_cache
@login_required
def index(request):
    return render_to_response('tools/index.html',{'user':request.user})
