#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2012  Andrew Colin Kissa <andrew@topdog.za.net>
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

class Searchengines(models.Model):
    name = models.TextField(unique=True)
    class Meta:
        app_label = 'web'
        managed = False

class UrlfilterSrc(models.Model):
    name = models.TextField(unique=True)
    class Meta:
        app_label = 'web'
        managed = False

class UrlfilterDst(models.Model):
    name = models.TextField(unique=True)
    class Meta:
        app_label = 'web'
        managed = False

class UrlfilterTimeslot(models.Model):
    name = models.TextField(unique=True)
    class Meta:
        app_label = 'web'
        managed = False


class Site(models.Model):
    '''A Site instance represents a site visited on a specific day.'''
    id = models.BigIntegerField(primary_key=True)
    date = models.DateField(unique=True)
    site = models.CharField(max_length=765)
    category = models.TextField(blank=True)
    category.help_text = 'To which category this site has been classified by the urlfilter. E.g. www.google.com might be searchengines.'
    def __unicode__(self):    
        return self.site
    class Meta:
        app_label = 'web'
        db_table = u'sites'
        managed = False 
        ordering = ['-id']


class AuthUser(models.Model):
    '''A User instance represents a proxy user on a specific day.'''
    id = models.BigIntegerField(primary_key=True)
    authuser = models.CharField(max_length=150)
    authuser.help_text = "Username used to authenticate to the webfilter. If no authentication was required, username is set as '-'"
    date = models.DateField(unique=True)
    date.help_text = 'Date when the user authenticated.'
    def __unicode__(self):    
        return self.authuser
    class Meta:
        app_label = 'web'
        db_table = u'users'
        managed = False
        ordering = ['-date','-id']

class Searchquery(models.Model):
    '''A search query which was detected by extendmysardb.py
    in an http request to one of the supported search engines.'''
    query = models.TextField(primary_key=True)
    query.help_text = 'Search query itself.'
    traffic = models.ForeignKey('Traffic', db_column='trafficID')
    traffic.help_text = 'Related traffic instance.'
    searchengine = models.TextField(blank=True)
    searchengine.help_text = 'Search engine queried.'
    def __unicode__(self):    
        return self.query
    class Meta:
        app_label = 'web'
        db_table = u'searchQueries'
        managed = False
        ordering = ['-traffic__id']
        verbose_name_plural = "Searchqueries"


class Urlfilterdeny(models.Model):
    '''A Urlfilterdeny instance represents an url
    which was by blocked by the Webfilter urlfiltering component.'''
    src = models.TextField(primary_key=True)
    src.help_text = '''Urlfilter source group for this request,
                    this is the squidguard "source acl".
                    Example: sales. Squidguard destination is logged in the s'''
    traffic = models.ForeignKey('Traffic',db_column='trafficID')
    traffic.help_text  = 'Web request which was blocked by the urflilter.'
    class Meta:
        app_label = 'web'
        db_table = u'urlfilterDenies'
        verbose_name_plural = "Urlfilterdenies"
        managed = False 
        ordering = ['-traffic__id']


class Virusdetection(models.Model):
    '''A Virusdetection instance represents a virus detected
    and blocked by the Webfilter antivirus component.'''
    virusname = models.TextField(primary_key=True, db_column='virusName')
    virusname.help_text = 'Name of the detected virus.'
    traffic = models.ForeignKey('Traffic',db_column='trafficID')
    traffic.help_text  = 'Web request in which the virus was detected.'
    def __unicode__(self):    
        return self.virusname
    class Meta:
        app_label = 'web'
        db_table = u'virusDetections'
        managed = False
        ordering = ['-traffic__id']

class Hostname(models.Model):
    '''A hostname instance represents an ip which was
    resolved to a hostname, by the mysar resolver cronjob.'''
    id = models.BigIntegerField(primary_key=True)
    ip = models.IntegerField(unique=True)
    ip.help_text = 'Ip address in integer format, parsed from logfiles. Has to be resolved to an hostname.'
    description = models.CharField(max_length=150)
    description.help_text = 'Not sure what this is used for.'
    isresolved = models.IntegerField(db_column='isResolved')
    isresolved.help_text = 'Wether this ip is already resolved to an hostname.'
    hostname = models.CharField(max_length=765)
    hostname.help_text = 'Hostname as resolved from ip address.'
    def __unicode__(self):    
        return self.hostname
    class Meta:
        app_label = 'web'
        db_table = u'hostnames'
        managed = False
        ordering = ['-id']


class Traffic(models.Model):
    '''A Traffic instance represents a http (web) request.'''
    id = models.BigIntegerField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    ip = models.ForeignKey(Hostname, db_column='ip',to_field='ip') 
    ip.help_text = "Request source ip address, in decimal format. Example: 3232300670."
    resultcode = models.CharField(max_length=150, db_column='resultCode')
    resultcode.help_text = "Proxy http response code for this request. Example: TCP_DENIED/407."
    bytes = models.BigIntegerField()
    bytes.help_text = "Size of the request response in bytes."
    url = models.TextField()
    url.help_text = "Request destination url."
    authuser = models.CharField(max_length=90)
    authuser.help_text = "Request source username. Only available if proxy authentication is enabled, else this is set to '-'."
    site = models.ForeignKey(Site, db_column='sitesID')
    site.help_text = "Request target Site instance."
    user = models.ForeignKey(AuthUser, db_column='usersID')
    user.help_text = "Request Source user instance."

    # status
    def _status(self):
        if self.virusdetection_set.count() > 0:
            return 'virus detected' 
        if self.urlfilterdeny_set.count() > 0:
            return 'url filtered'
        if self.searchquery_set.count() > 0:
            return 'search query'  
        return 'normal'
    
    status = property(_status)

    def _urlfilter(self):
        return self.urlfilterdeny_set.count()

    urlfilter = property(_urlfilter)

    def _virusdetection(self):
        return self.virusdetection_set.count()

    virusdetection = property(_virusdetection)

    def _searchquery(self):
        return self.searchquery_set.count()

    searchquery = property(_searchquery)

    def _searchitems(self):
        return self.searchquery_set.all()

    searchitems = property(_searchitems)
    
    def _urlitems(self):
        return self.urlfilterdeny_set.all()

    urlitems = property(_urlitems)

    def _virusitems(self):
        return self.virusdetection_set.all()

    virusitems = property(_virusitems)

    def _css(self):
        "CSS"
        if self.virusdetection_set.count() > 0:
            return 'web_virus_detected' 
        if self.urlfilterdeny_set.count() > 0:
            return 'web_url_filtered'
        if self.searchquery_set.count() > 0:
            return 'web_search_query'  
        return 'LightBlue_div'

    css = property(_css)

    class Meta:
        app_label = 'web'
        db_table = u'traffic'
        managed = False
        ordering = ['-id']

class UrlfilterInfo(models.Model):
    src = models.ForeignKey('UrlfilterSrc')
    dst = models.ForeignKey('UrlfilterDst')
    timeslot = models.ForeignKey('UrlfilterTimeslot')
    denied = models.BooleanField()
    denied.default = False
    traffic = models.ForeignKey(Traffic, db_column='trafficID')
    class Meta:
        app_label = 'web'
        db_table = 'urlfilterDenies'
        managed = False

class SearchqueryInfo(models.Model):
    '''A search query which was detected by extendmysardb.py
    in an http request to one of the supported search engines.'''
    # query
    query = models.TextField()
    query.help_text = 'Search query itself.'
    # searchengine
    searchengine = models.ForeignKey('Searchengines')
    searchengine.help_text = 'Search engine queried.'
    traffic = models.ForeignKey(Traffic, db_column='trafficID')
    class Meta:
        app_label = 'web'
        db_table = 'searchQueries'
        managed = False

class VirusdetectionInfo(models.Model):
    '''A VirusdetectionInfo instance represents a virus detected
    and blocked by the Webfilter antivirus component.'''
    virusname = models.TextField(unique=True)
    virusname.help_text = 'Name of the detected virus.'
    traffic = models.ForeignKey(Traffic, db_column='trafficID')
    class Meta:
        app_label = 'web'
        db_table = 'virusDetections'
        managed = False
