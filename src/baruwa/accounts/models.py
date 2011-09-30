#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2011  Andrew Colin Kissa <andrew@topdog.za.net>
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


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.html import strip_tags

from baruwa.fixups.models import SignatureImg
from baruwa.utils.html import SignatureCleaner

UNCLEANTAGS = ['html', 'head', 'link', 'body', 'base']


class UserAddresses(models.Model):
    """
    email and domain addresses
    """
    ADDRESS_TYPES = (
        (1, 'Domain'),
        (2, 'email'),
    )
    id = models.AutoField(primary_key=True)
    address = models.CharField(unique=True, max_length=255)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User)
    address_type = models.IntegerField(choices=ADDRESS_TYPES, default=2)
    load_balance = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_addresses'

    def __unicode__(self):
        return u'%d' % self.user.id

    def save(self):
        ""
        account = UserProfile.objects.get(user=self.user)
        if account.account_type == 2:
            self.address_type = 1
        else:
            self.address_type = 2
        super(UserAddresses, self).save()


class UserProfile(models.Model):
    """
    user profiles
    """
    ACCOUNT_TYPES = (
        (1, 'Administrator'),
        (2, 'Domain Admin'),
        (3, 'User'),
    )

    id = models.AutoField(primary_key=True)
    send_report = models.BooleanField(default=True)
    scan_mail = models.BooleanField(default=True)
    sa_high_score = models.IntegerField(default=0)
    sa_low_score = models.IntegerField(default=0)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=3)
    user = models.ForeignKey(User, unique=True)

    class Meta:
        db_table = 'profiles'

    def __unicode__(self):
        return u"User profile for: " + self.user.username


def create_user_profile(sender, **kwargs):
    """
    create_user_profile
    """
    user = kwargs['instance']
    if kwargs.get('created', False):
        UserProfile.objects.get_or_create(user=user)
    else:
        profile = UserProfile.objects.get(user=user)
        if user.is_superuser:
            profile.account_type = 1
            profile.save()

#def delete_user_profile(sender, **kwargs):
#    """delete_user_profile"""
#    user = kwargs['instance']


class UserSignature(models.Model):
    "User Email signatures"
    id = models.AutoField(primary_key=True)
    signature_type = models.IntegerField()
    signature_content = models.TextField(blank=False)
    enabled = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='us_ur')
    image = models.ForeignKey(SignatureImg, blank=True, null=True,
                                related_name='us_si')

    def clean(self):
        "sanitize inputs"
        if self.signature_type == 1:
            self.signature_content = strip_tags(self.signature_content)
        else:
            cleaner = SignatureCleaner(remove_tags=UNCLEANTAGS,
                                        safe_attrs_only=False)
            self.signature_content = cleaner.clean_html(self.signature_content)

    class Meta:
        db_table = 'user_signatures'
        unique_together = ('user', 'signature_type')


post_save.connect(create_user_profile, sender=User)
