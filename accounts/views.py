from django.contrib.auth import logout
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from accounts.models import Users,UserFilters
from accounts.forms import AccountAddForm

@never_cache
@login_required
def index(request,page=1,direction='dsc',order_by='username'):
    ordering = order_by
    if direction == 'dsc':
        ordering = order_by
        order_by = "-%s" % order_by
    if request.method == 'POST':
        form = AccountAddForm(request.POST)
        #if form.is_valid():
        #    clean_data = form.cleaned_data
        #    u = Users(username=cleaned_data['username'],password=cleaned_data['password'],fullname=cleaned_data['fullname'],
        #        type=cleaned_data['type'],quarantine_report=cleaned_data['quarantine_report'],spamscore=cleaned_data['spamscore'],
        #        highspamscore=cleaned_data['highspamscore'],noscan=cleaned_data['noscan'],quarantine_rcpt=cleaned_data['quarantine_rcpt'])
        #    try:
        #        u.save()
        #    except:
        #        error_msg = 'Account creation failed'
    else:
        form = AccountAddForm()
    user_list = Users.objects.all()
    return object_list(request,template_name='accounts/index.html',queryset=user_list,paginate_by=10,page=page,
        extra_context={'quarantine':0,'direction':direction,'order_by':ordering,'app':'accounts','active_filters':[],'list_all':1,'form':form})
