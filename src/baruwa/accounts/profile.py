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

from baruwa.accounts.models import UserProfile, UserAddresses
from baruwa.accounts.forms import UserProfileForm
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re

def retrieve_profile(user):
    "get or create a profile"
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        if user.is_superuser:
            account_type = 1
        else:
            account_type = 3
        profile = UserProfile(user=user, account_type=account_type)
        profile.save()
    return profile
    
def set_profile(request):
    "save a profile"
    profile = retrieve_profile(request.user)
    profile_form = UserProfileForm(request.POST, instance=profile)
    profile_form.save()
    
def set_user_addresses(request):
    """
    set addresses in the session
    """
    if not request.user.is_superuser:
        profile = retrieve_profile(request.user)
        addresses = [ addr.address for addr in UserAddresses.objects.filter(
            user=request.user).exclude(enabled__exact=0)]
        if profile.account_type == 3:
            if email_re.match(request.user.username):
                addresses.append(request.user.username)
        request.session['user_filter'] = {'account_type':profile.account_type, 
            'addresses':addresses}
        
        