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
from django.utils.html import strip_tags

from baruwa.fixups.models import SignatureImg
from baruwa.utils.html import SignatureCleaner
from baruwa.accounts.models import UserAddresses

UNCLEANTAGS = ['html', 'head', 'link', 'body', 'base']


class MailHost(models.Model):
    """Mail hosts"""
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    port = models.IntegerField(default=25)
    useraddress = models.ForeignKey(UserAddresses, related_name='mh_ua')

    class Meta:
        db_table = 'mail_hosts'

    def __unicode__(self):
        return u"Mail host " + self.address


class MailAuthHost(models.Model):
    "Holds authentication hosts"

    AUTH_TYPE = (
        (1, 'POP3'),
        (2, 'IMAP'),
        (3, 'SMTP'),
        (4, 'RADIUS/RSA SECUREID')
    )

    address = models.CharField(max_length=255)
    protocol = models.IntegerField(choices=AUTH_TYPE, default=1)
    port = models.IntegerField(blank=True)
    enabled = models.BooleanField(default=True)
    split_address = models.BooleanField()
    useraddress = models.ForeignKey(UserAddresses, related_name='mah_ua')

    class Meta:
        db_table = 'auth_hosts'


class ScannerHost(models.Model):
    "Holds scanning nodes"
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)

    class Meta:
        db_table = 'scanners'


class ConfigSection(models.Model):
    "MailScanner configuration sections"
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'scanner_config_sections'


class ScannerConfig(models.Model):
    "Configuration container"
    id = models.AutoField(primary_key=True)
    internal = models.CharField(max_length=255)
    external = models.CharField(max_length=255)
    display = models.TextField()
    help = models.TextField()
    value = models.TextField()
    section = models.ForeignKey(ConfigSection)
    host = models.ForeignKey(ScannerHost)

    class Meta:
        db_table = 'scanner_config'
        unique_together = ('internal', 'host')


class DomainSignature(models.Model):
    "Email signatures"
    id = models.AutoField(primary_key=True)
    signature_type = models.IntegerField()
    signature_content = models.TextField(blank=False)
    enabled = models.BooleanField(default=False)
    useraddress = models.ForeignKey(UserAddresses, related_name='ds_ua')
    image = models.ForeignKey(SignatureImg, blank=True, null=True,
                                related_name='ds_si')

    def clean(self):
        "sanitize inputs"
        if self.signature_type == 1:
            self.signature_content = strip_tags(self.signature_content)
        else:
            cleaner = SignatureCleaner(remove_tags=UNCLEANTAGS,
                                        safe_attrs_only=False)
            self.signature_content = cleaner.clean_html(self.signature_content)

    class Meta:
        db_table = 'domain_signatures'
        unique_together = ('useraddress', 'signature_type')

