#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# vim: ai ts=4 sts=4 et sw=4

from django.db import models

# Create your models here.
class Maillog(models.Model):
    timestamp = models.DateTimeField()
    id = models.TextField(blank=True, primary_key=True)
    size = models.IntegerField(null=True, blank=True)
    from_address = models.TextField(blank=True)
    from_domain = models.TextField(blank=True)
    to_address = models.TextField(blank=True)
    to_domain = models.TextField(blank=True)
    subject = models.TextField(blank=True)
    clientip = models.TextField(blank=True)
    archive = models.TextField(blank=True)
    isspam = models.IntegerField(null=True, blank=True)
    ishighspam = models.IntegerField(null=True, blank=True)
    issaspam = models.IntegerField(null=True, blank=True)
    isrblspam = models.IntegerField(null=True, blank=True)
    isfp = models.IntegerField(null=True, blank=True)
    isfn = models.IntegerField(null=True, blank=True)
    spamwhitelisted = models.IntegerField(null=True, blank=True)
    spamblacklisted = models.IntegerField(null=True, blank=True)
    sascore = models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)
    spamreport = models.TextField(blank=True)
    virusinfected = models.IntegerField(null=True, blank=True)
    nameinfected = models.IntegerField(null=True, blank=True)
    otherinfected = models.IntegerField(null=True, blank=True)
    report = models.TextField(blank=True)
    ismcp = models.IntegerField(null=True, blank=True)
    ishighmcp = models.IntegerField(null=True, blank=True)
    issamcp = models.IntegerField(null=True, blank=True)
    mcpwhitelisted = models.IntegerField(null=True, blank=True)
    mcpblacklisted = models.IntegerField(null=True, blank=True)
    mcpsascore = models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)
    mcpreport = models.TextField(blank=True)
    hostname = models.TextField(blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TextField(blank=True) # This field type is a guess.
    headers = models.TextField(blank=True)
    quarantined = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'maillog'
        get_latest_by = "timestamp"
        ordering = ['-timestamp']

    def __unicode__(self):
	      return self.id

    @models.permalink 
    def get_absolute_url(self):
        return('message-detail',(),{'message_id':self.id})
    
    @models.permalink
    def get_preview_url(self):
        return('preview-message',(),{'message_id':self.id})

    @models.permalink
    def get_wl_url(self):
        return('whitelist-sender',(),{'message_id':self.id})

    @models.permalink
    def get_bl_url(self):
        return('blacklist-sender',(),{'message_id':self.id})

class SaRules(models.Model):
    rule = models.CharField(max_length=100, primary_key=True)
    rule_desc = models.CharField(max_length=200)
    class Meta:
        db_table = u'sa_rules'
