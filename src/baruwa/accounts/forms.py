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

from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext_lazy as _
from baruwa.accounts.models import UserProfile, UserAddresses
from baruwa.utils.regex import DOM_RE
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re
from baruwa.utils.regex import ADDRESS_RE

class PwResetForm(PasswordResetForm):
    """
        Overload the password reset form to prevent admin and
        external accounts from being reset via the interface
    """
    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        and the user is not an external auth user or admin user
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(email__iexact=email)
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have"
            " an associated user account. Are you sure you've registered?"))
        for user in self.users_cache:
            if not user.has_usable_password():
                raise forms.ValidationError(_("That e-mail address belongs to"
                " an externally authenticated account. Please change the"
                " password on that external system."))
                break
            if user.is_superuser:
                raise forms.ValidationError(_("That e-mail address belongs to"
                " an admin account. Please use the manage.py command to reset"))
                break
        return email
    
    
class UserProfileForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    user_id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = UserProfile
        exclude = ('user',)

        
class OrdUserProfileForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    user_id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = UserProfile
        exclude = ('user', 'account_type')

        
class UserCreateForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text = _(
            "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages = {'invalid': _(
            "This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
            
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            _("A user with that username already exists."))

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
        
    class Meta:
        model = User
        exclude = ('is_staff', 'last_login', 'date_joined', 
            'groups', 'user_permissions',)

        
class UserAddressForm(forms.ModelForm):
    """
    Used by admin to associate addresses or domains.
    """
    address = forms.RegexField(regex=ADDRESS_RE, 
        widget=forms.TextInput(attrs={'size':'50'}))
    
    def clean(self):
        """clean_address"""
        if self._errors: 
            return
            
        cleaned_data = self.cleaned_data   
        address = cleaned_data['address']
        user = cleaned_data['user']
        if user.is_superuser:
            error_msg = _('Super users do not use addresses')
            self._errors["address"] = ErrorList([error_msg])
            del cleaned_data['address']
        account = UserProfile.objects.get(user=user)
        if account.account_type == 2:
            if not DOM_RE.match(address):
                error_msg = _('provide a valid domain address')
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        else:
            if not email_re.match(address):
                error_msg = _('provide a valid email address')
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        return cleaned_data
        
    class Meta:
        model = UserAddresses
        exclude = ('id', 'address_type')

        
class EditAddressForm(forms.ModelForm):
    "Edit address"
    address = forms.RegexField(
        regex=ADDRESS_RE, widget=forms.TextInput(attrs={'size':'50'}))
    
    def clean(self):
        """clean_address"""
        if self._errors: 
            return
            
        cleaned_data = self.cleaned_data   
        address = cleaned_data['address']
        user = cleaned_data['user']
        if user.is_superuser:
            error_msg = _('Super users do not use addresses')
            self._errors["address"] = ErrorList([error_msg])
            del cleaned_data['address']
        account = UserProfile.objects.get(user=user)
        if account.account_type == 2:
            if not DOM_RE.match(address):
                error_msg = _('provide a valid domain address')
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        else:
            if not email_re.match(address):
                error_msg = _('provide a valid email address')
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        return cleaned_data    
           
    class Meta:
        model = UserAddresses
        exclude = ('id', 'address_type')

        
class DeleteAddressForm(forms.ModelForm):
    "Delete address"
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = UserAddresses
        exclude = ('address', 'enabled', 'user')

        
class UserUpdateForm(forms.ModelForm):
    """
    Allows users to update thier account info. 
    """
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = User
        exclude = ('last_login', 'date_joined', 'username', 
            'groups', 'is_superuser', 'user_permissions', 
            'is_staff', 'password', 'is_active')
            

class AdminUserUpdateForm(forms.ModelForm):
    """
    Allows the admins to manage account info
    """
    username = forms.RegexField(label=_("Username"), 
        max_length=30, regex=r'^[\w.@+-]+$',
            help_text = _(
            "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages = {'invalid': _(
            "This value may contain only letters, numbers and @/./+/-/_ characters.")})
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 
            'last_name', 'email', 'is_superuser', 'is_active')

        
class DeleteUserForm(forms.ModelForm):
    """DeleteUserForm"""
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = User
        exclude = ('last_login', 'date_joined', 'username', 
            'groups', 'is_superuser', 'user_permissions', 
            'is_staff', 'password', 'is_active', 'first_name', 
            'last_name', 'email')
        #fields = ('id')
        