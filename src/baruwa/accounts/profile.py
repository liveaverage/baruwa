from baruwa.accounts.models import UserProfile, UserAddresses
from baruwa.accounts.forms import UserProfileForm
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re

def retrieve_profile(user):
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        if user.is_superuser:
            account_type=1
        else:
            account_type=3
        profile = UserProfile(user=user, account_type=account_type)
        profile.save()
    return profile
    
def set_profile(request):
    profile = retrieve_profile(request.user)
    profile_form = UserProfileForm(request.POST, instance=profile)
    profile_form.save()
    
def set_user_addresses(request):
    """
    """
    addresses = []
    if not request.user.is_superuser:
        profile = retrieve_profile(request.user)
        for addr in UserAddresses.objects.filter(user=request.user).exclude(enabled__exact=0):
            addresses.append(addr.address)
        if profile.account_type == 3:
            if email_re.match(request.user.username):
                addresses.append(request.user.username)
        request.session['user_filter'] = {'account_type':profile.account_type, 'addresses':addresses}
        
        