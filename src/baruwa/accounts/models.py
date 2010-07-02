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
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserAddresses(models.Model):
    """
    """
    id = models.IntegerField(primary_key=True)
    address = models.CharField(unique=True, max_length=255)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User)

    class Meta:
        db_table = 'user_addresses'

    def __unicode__(self):
        return u"Address for user "+ self.user.username
        
class UserProfile(models.Model):
    """
    """
    ACCOUNT_TYPES = (
        (1, 'Administrator'),
        (2, 'Domain Admin'),
        (3, 'User'),
    )
    
    id = models.IntegerField(primary_key=True)
    send_report = models.BooleanField(default=True)
    scan_mail = models.BooleanField(default=True)
    sa_high_score = models.IntegerField(default=0)
    sa_low_score = models.IntegerField(default=0)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=3)
    user = models.ForeignKey(User, unique=True)
    
    class Meta:
        db_table = 'profiles'
            
    def __unicode__(self):
        return u"User profile for: "+ self.user.username

def create_user_profile(sender, **kwargs):
    """
    create_user_profile
    """
    user = kwargs['instance']
    if kwargs.get('created', False): 
        UserProfile.objects.get_or_create(user=user)
        
#def delete_user_profile(sender, **kwargs):
#    """delete_user_profile"""
#    user = kwargs['instance']
    

post_save.connect(create_user_profile, sender=User)