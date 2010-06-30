from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserAddresses(models.Model):
    """
    """
    id = models.IntegerField(primary_key=True)
    address = models.TextField(unique=True)
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