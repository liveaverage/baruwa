from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from baruwa.accounts.models import UserProfile, UserAddresses
from baruwa.lists.forms import dom_re
import re
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re

address_re = re.compile(
r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  
r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")' 
r'@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$'
r'|^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)


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
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
            
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
        
    class Meta:
        model = User
        exclude = ('is_staff', 'last_login', 'date_joined', 'groups', 'user_permissions',)
        
class UserAddressForm(forms.ModelForm):
    """
    Used by admin to associate addresses or domains.
    """
    address = forms.RegexField(regex=address_re, widget=forms.TextInput(attrs={'size':'50'}))
    
    def clean(self):
        """clean_address"""
        if self._errors: 
            return
            
        cleaned_data = self.cleaned_data   
        address = cleaned_data['address']
        user = cleaned_data['user']
        if user.is_superuser:
            error_msg = 'Super users do not use addresses'
            self._errors["address"] = ErrorList([error_msg])
            del cleaned_data['address']
        account = UserProfile.objects.get(user=user)
        if account.account_type == 2:
            if not dom_re.match(address):
                error_msg = 'provide a valid domain address'
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        else:
            if not email_re.match(address):
                error_msg = 'provide a valid email address'
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        return cleaned_data
        
    class Meta:
        model = UserAddresses
        exclude = ('id')
        
class EditAddressForm(forms.ModelForm):
    "Edit address"
    address = forms.RegexField(regex=address_re, widget=forms.TextInput(attrs={'size':'50'}))
    
    def clean(self):
        """clean_address"""
        if self._errors: 
            return
            
        cleaned_data = self.cleaned_data   
        address = cleaned_data['address']
        user = cleaned_data['user']
        if user.is_superuser:
            error_msg = 'Super users do not use addresses'
            self._errors["address"] = ErrorList([error_msg])
            del cleaned_data['address']
        account = UserProfile.objects.get(user=user)
        if account.account_type == 2:
            if not dom_re.match(address):
                error_msg = 'provide a valid domain address'
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        else:
            if not email_re.match(address):
                error_msg = 'provide a valid email address'
                self._errors["address"] = ErrorList([error_msg])
                del cleaned_data['address']
        return cleaned_data    
           
    class Meta:
        model = UserAddresses
        exclude = ('id')
        
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
        exclude = ('last_login', 'date_joined', 'username', 'groups', 'is_superuser', 'user_permissions', 'is_staff', 'password', 'is_active')
        
class AdminUserUpdateForm(forms.ModelForm):
    """
    Allows the admins to manage account info
    """
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
            help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
            error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_active')
        
class DeleteUserForm(forms.ModelForm):
    """DeleteUserForm"""
    id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = User
        exclude = ('last_login', 'date_joined', 'username', 'groups', 'is_superuser', 'user_permissions', 'is_staff', 'password', 'is_active', 'first_name', 'last_name', 'email')
        #fields = ('id')
        