from django.shortcuts import render_to_response,get_object_or_404
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from accounts.models import Users
from accounts.forms import UserForm
try:
    import hashlib as md5
except ImportError:
    import md5

@never_cache
@login_required
def index(request,page=1,direction='dsc',order_by='username'):
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
            m = md5.new(new_user.password)
            hashv = m.hexdigest()
            new_user.password = hashv
            form = UserForm()
            new_user.save()

    else:
        form = UserForm()
    user_list = Users.objects.all()
    return object_list(request,template_name='accounts/index.html',queryset=user_list,paginate_by=10,page=page,
        extra_context={'quarantine':0,'direction':direction,'order_by':ordering,'app':'accounts','active_filters':[],'list_all':1,'form':form})

@never_cache
@login_required
def user_account(request,user_name):
    user_object = get_object_or_404(Users,pk=user_name)
    if request.method == 'POST':
        form = UserForm(request.POST,instance=user_object)
        try:
            form.save()
        except:
            error_msg = 'The account could not be updated'
        else:
            user_object = get_object_or_404(Users,pk=user_name)
            form = UserForm(instance=user_object)
    else:
        form = UserForm(instance=user_object)
    return render_to_response('accounts/user.html',{'user':request.user,'form':form})
