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
from django.db.models import Q

class MessageManager(models.Manager):        
    def for_user(self, request):
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(MessageManager, self).get_query_set().filter(Q(from_domain__in=addresses) | Q(to_domain__in=addresses))
            if account_type == 3:
                return super(MessageManager, self).get_query_set().filter(Q(from_address__in=addresses) | Q(to_address__in=addresses))
        return super(MessageManager, self).get_query_set()

class QuarantineMessageManager(models.Manager):
    """
    QuarantineMessageManager
    """
    def for_user(self, request):
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(QuarantineMessageManager, self).get_query_set().filter(Q(from_domain__in=addresses) | Q(to_domain__in=addresses)).filter(isquarantined__exact=1)
            if account_type == 3:
                return super(QuarantineMessageManager, self).get_query_set().filter(Q(from_address__in=addresses) | Q(to_address__in=addresses)).filter(isquarantined__exact=1)
        return super(QuarantineMessageManager, self).get_query_set().filter(isquarantined__exact=1)
        
class EmailReportMessageManager(models.Manager):
    "Used in processing the quarantine email reports"
    def for_user(self, addresses, account_type):
        if account_type == 1:
            return super(EmailReportMessageManager, self).get_query_set().filter(isquarantined__exact=1)
        elif account_type == 2:
            return super(EmailReportMessageManager, self).get_query_set().filter(Q(from_domain__in=addresses) | Q(to_domain__in=addresses)).filter(isquarantined__exact=1)
        else:
            return super(EmailReportMessageManager, self).get_query_set().filter(Q(from_address__in=addresses) | Q(to_address__in=addresses)).filter(isquarantined__exact=1)

class Message(models.Model):
    """
    Message Model, represents messages in the
    Database.
    """

    id = models.CharField(max_length=255, primary_key=True)
    actions = models.CharField(max_length=255)
    clientip = models.IPAddressField()
    date = models.DateField()
    from_address = models.CharField(blank=True, db_index=True)
    from_domain = models.CharField(db_index=True)
    headers = models.TextField()
    hostname = models.TextField()
    highspam = models.IntegerField(default=0, db_index=True)
    rblspam = models.IntegerField(default=0)
    saspam = models.IntegerField(default=0)
    spam = models.IntegerField(default=0, db_index=True)
    nameinfected = models.IntegerField(default=0)
    otherinfected = models.IntegerField(default=0)
    isquarantined = models.IntegerField(default=0, db_index=True)
    sascore = models.FloatField()
    scaned = models.IntegerField(default=0)
    size = models.IntegerField()
    blacklisted = models.IntegerField(default=0, db_index=True)
    spamreport = models.TextField(blank=True)
    whitelisted = models.IntegerField(default=0, db_index=True)
    subject = models.TextField(blank=True)
    time = models.TimeField()
    timestamp = models.DateTimeField()
    to_address = models.CharField(db_index=True)
    to_domain = models.CharField(db_index=True)
    virusinfected = models.IntegerField(default=0)
    
    objects = models.Manager()
    messages = MessageManager()
    quarantine = QuarantineMessageManager()
    quarantine_report = EmailReportMessageManager()
    
    class Meta:
        db_table = 'messages'
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']

    def __unicode__(self):
        return u"Message id: "+ self.id
        
    def can_access(self, request):
        """can_access"""
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            addresses = request.session['user_filter']['addresses']
            if account_type == 2:
                if ('@' not in self.to_address) and ('@' not in self.from_address):
                    return False
                else:
                    dom1 = self.to_address.split('@')[1]
                    dom2 = self.from_address.split('@')[1]
                    if (dom1 not in addresses) and (dom2 not in addresses):
                        return False
                return True
            if account_type == 3:
                addresses = request.session['user_filter']['addresses']
                if (self.to_address not in addresses) and (self.from_address not in addresses):
                    return False
        return True

class SaRules(models.Model):
    rule = models.CharField(max_length=25, primary_key=True)
    rule_desc = models.CharField(max_length=200)

    class Meta:
        db_table = u'sa_rules'