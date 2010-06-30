from django import forms
from django.forms.util import ErrorList
from django.template.defaultfilters import force_escape
import re
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re
    
LIST_TYPES = (
    ('1', 'Whitelist'),
    ('2', 'Blacklist'),
)
dom_re = re.compile(r'^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)
ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
user_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*)$", re.IGNORECASE)

class ListAddForm(forms.Form):
    """ListAddForm"""
    
    list_type = forms.ChoiceField(choices=LIST_TYPES)
    from_address = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))
    to_address = forms.CharField(required=False)
        
    def __init__(self, request=None, *args, **kwargs):
        super(ListAddForm, self).__init__(*args, **kwargs)
        self.request = request
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            addresses = request.session['user_filter']['addresses']
            load_addresses = []
            if addresses:
                for address in addresses:
                    load_addresses.append((address, address))
            self.fields['to_address'] = forms.ChoiceField(choices=load_addresses)

    def clean_to_address(self):
        to_address = self.cleaned_data['to_address']
        if not email_re.match(to_address):
            raise forms.ValidationError('%s provide a valid e-mail address' % force_escape(to_address))
        if to_address not in self.request.session['user_filter']['addresses'] and not self.request.user.is_superuser():
            raise forms.ValidationError("The address: %s does not belong to you." % force_escape(to_address))
        return to_address
    
    def clean_from_address(self):
        from_address = self.cleaned_data['from_address']
        from_address = from_address.strip()

        if not email_re.match(from_address) and not dom_re.match(from_address) and not ipv4_re.match(from_address):
            raise forms.ValidationError("Provide either a valid IPv4, email, Domain address")
        return from_address
        
class AdminListAddForm(ListAddForm):
    """AdminListAddForm"""
    
    user_part = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(AdminListAddForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            account_type = self.request.session['user_filter']['account_type']
            addresses = self.request.session['user_filter']['addresses']
            load_addresses = []
            if addresses:
                for address in addresses:
                    load_addresses.append((address, address))
            self.fields['to_address'] = forms.ChoiceField(choices=load_addresses)
        else:
            self.fields['to_address'].widget=forms.TextInput(attrs={'size':'24'})
     
    def clean_to_address(self):
        """clean_to_address"""
        to_address = self.cleaned_data['to_address']
        try:
            to_address = to_address.strip()
        except:
            pass
        if not self.request.user.is_superuser:
            account_type = self.request.session['user_filter']['account_type']
            addresses = self.request.session['user_filter']['addresses']
            if to_address not in addresses:
                raise forms.ValidationError("The address: %s does not belong to you." % force_escape(to_address))
        
        if to_address != "" and not to_address is None:
            if not dom_re.match(to_address):
                raise forms.ValidationError("Provide either a valid domain")
        else:
            to_address = 'any'
        
        return to_address
        
    def clean_user_part(self):
        """clean_user_part"""
        user_part = self.cleaned_data['user_part']
        
        if user_part == '' or user_part is None:
            user_part = 'any'
        else:
            user_part = user_part.strip()
            if not user_re.match(user_part):
                raise forms.ValidationError('provide a valid user part of the email address')
        return user_part
        
class FilterForm(forms.Form):
    query_type = forms.ChoiceField(choices=((1,'containing'),(2,'excluding')))
    search_for = forms.CharField(required=False)
    
class ListDeleteForm(forms.Form):
    list_item = forms.CharField(widget=forms.HiddenInput)
    
        