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

"Config tasks"
import os
import base64
import socket

from celery.task import Task
from lxml.html import tostring, fragments_fromstring, iterlinks

from django.conf import settings
from django.db import DatabaseError
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.utils.translation import ugettext as _

from baruwa.utils.html import SignatureCleaner
from baruwa.utils.mail.message import TestDeliveryServers
from baruwa.config.models import (UNCLEANTAGS, SignatureImg,
DomainSignature, ScannerConfig, ScannerHost, ConfigSection)
from baruwa.accounts.models import UserSignature, UserAddresses


def update_ms_serial(logger):
    """Update MS configuration serial"""
    hostname = socket.gethostname()
    host = ScannerHost.objects.filter(address=hostname)[0]
    section = ConfigSection.objects.get(pk=28)
    msconfig = ScannerConfig.objects.filter(
                internal='confserialnumber',
                host=host,
                )[0]
    if msconfig:
        msconfig.value = (int(msconfig.value) + 1)
    else:
        msconfig = ScannerConfig(
                                value=1,
                                host=host,
                                internal='confserialnumber',
                                external='confserialnumber',
                                section=section,
                                )
    try:
        msconfig.save()
        logger.info(_("Notified %(h)s of config update") %
                    dict(h=hostname))
    except DatabaseError:
        logger.info(_("Failed to notify %(h)s of config update") %
                    dict(h=hostname))


class TestSMTPServer(Task):
    "Tests a delivery server"
    name = 'test-smtp-server'
    serializer = 'json'

    def run(self, host, port, from_addr,
        to_addr, host_id, count=None, **kwargs):
        "run"
        result = {'errors': {}, 'host': host_id}
        logger = self.get_logger(**kwargs)
        logger.info(_("Starting connection tests to: %(host)s") % {
        'host': host})
        server = TestDeliveryServers(host, port, to_addr, from_addr)
        if server.ping(count):
            result['ping'] = True
        else:
            result['ping'] = False
            result['errors']['ping'] = ' '.join(server.errors)
            server.reset_errors()
        if server.smtp_test():
            result['smtp'] = True
        else:
            result['smtp'] = False
            result['errors']['smtp'] = ' '.join(server.errors)
        return result


def write_text_sig(sigfile, sig, logger):
    "write txt sig"
    sighandle = open(sigfile, 'w')
    if not sig.signature_content.startswith('--'):
        sighandle.write("\n--\n")
    sighandle.write(sig.signature_content)
    sighandle.close()
    logger.info(_("Wrote text signature: %(sig)s") % dict(sig=sigfile))


def write_html_sig(sigfile, sig, basedir, is_domain, logger):
    "write html sig"
    cleaner = SignatureCleaner(style=True, remove_tags=UNCLEANTAGS,
                                safe_attrs_only=False)
    html = cleaner.clean_html(sig.signature_content)
    html = fragments_fromstring(html)[0]
    for element, attribute, link, pos in iterlinks(html):
        if link.startswith('/settings/imgs/'):
            view, args, kwargs = resolve(link)
            view = None
            args = None
            img = SignatureImg.objects.get(pk=kwargs['img_id'])
            if is_domain:
                imgfile = '%s/domains/imgs/%s' % (basedir, img.name)
            else:
                imgfile = '%s/users/imgs/%s' % (basedir, img.name)
            element.attrib['src'] = 'cid:%s' % img.name
            imghandle = open(imgfile, 'wb')
            imghandle.write(base64.decodestring(img.image))
            imghandle.close()
            logger.info(_("Wrote img: %(img)s") % dict(img=imgfile))
            # update the sig with image obtained
            sig.image = img
    if 'link' in locals():
        sig.save()
    sighandle = open(sigfile, 'w')
    if not sig.signature_content.startswith('--'):
        sighandle.write('<br/>--<br/>')
    sighandle.write(tostring(html))
    logger.info(_("Wrote html signature: %(sig)s") % dict(sig=sigfile))


class GenerateAccountSigs(Task):
    """Generate the signature files"""
    name = 'generate-user-signature-files'
    serializer = 'json'
    ignore_result = True

    def run(self, userid, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        # get user
        user = User.objects.get(pk=userid)
        if user:
            signatures = UserSignature.objects.filter(user=user, enabled=True)
            basedir = settings.EMAIL_SIGNATURES_DIR
            # process signatures
            logger.info(_("Processing signatures for: %(user)s") % 
                        dict(user=user.username))
            for sig in signatures:
                try:
                    if sig.signature_type == 1:
                        # text signature
                        sigfile = '%s/users/text/%d.txt' % (basedir, user.id)
                        write_text_sig(sigfile, sig, logger)
                    if sig.signature_type == 2:
                        # html signature
                        sigfile = '%s/users/html/%d.html' % (basedir, user.id)
                        write_html_sig(sigfile, sig, basedir, False, logger)
                except os.error, error:
                    logger.info(_("Error occured: %(err)s") %
                                dict(err=str(error)))
            if signatures:
                update_ms_serial(logger)
            logger.info(_("Finished processing signatures for: %(u)s") %
                        dict(u=user.username))
        else:
            logger.info(_('User with userid: %s not found') % user.id)

class GenerateDomainSigs(Task):
    """Generates email signatures for a domain"""
    name = 'generate-domain-signature-files'
    serializer = 'json'
    ignore_result = True

    def run(self, domainid, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        domain = UserAddresses.objects.get(pk=domainid)
        if domain:
            basedir = settings.EMAIL_SIGNATURES_DIR
            signatures = DomainSignature.objects.filter(useraddress=domain,
                                                        enabled=True)
            logger.info(_("Processing signatures for: %(d)s") %
                        dict(d=domain.address))
            for sig in signatures:
                try:
                    if sig.signature_type == 1:
                        sigfile = '%s/domains/text/%d.txt' % (basedir,
                                                            domain.id)
                        write_text_sig(sigfile, sig, logger)
                    if sig.signature_type == 2:
                        sigfile = '%s/domains/html/%d.html' % (basedir,
                                                            domain.id)
                        write_html_sig(sigfile, sig, basedir, True, logger)
                except os.error, error:
                    logger.info(_("Error occured: %(err)s") %
                                dict(err=str(error)))
            if signatures:
                update_ms_serial(logger)
            logger.info(_("Finished processing signatures for: %(d)s") %
                        dict(d=domain.address))
        else:
            logger.info(_('Domain with domainid: %s not found') % domainid)


class DeleteDomainSigs(Task):
    """Delete domains email signatures from filesystem"""
    name = 'delete-domain-signature-files'
    serializer = 'json'
    ignore_result = True

    def run(self, sigids, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        signatures = DomainSignature.objects.filter(id__in=sigids)
        if signatures:
            domain = signatures[0].useraddress.address
            domainid = signatures[0].useraddress.id
            logger.info(_("Deleting signatures for: %(d)s") % dict(d=domain))
            basedir = settings.EMAIL_SIGNATURES_DIR
            for sig in signatures:
                if sig.signature_type == 1:
                    sigfile = '%s/domains/text/%d.txt' % (basedir, domainid)
                elif sig.signature_type == 2:
                    sigfile = '%s/domains/html/%d.html' % (basedir, domainid)
                try:
                    os.unlink(sigfile)
                    sig.delete()
                except os.error, error:
                    logger.info(_("Error deleting %(f)s: %(e)s") %
                                dict(f=sigfile, e=str(error)))
            update_ms_serial(logger)
            logger.info(_("Finished deletion of signatures for: %(d)s") %
                        dict(d=domain))
        else:
            logger.info(_('Domain signatures not found'))


class DeleteAccountSigs(Task):
    """Delete accounts email signatures from filesystem"""
    name = 'delete-user-signature-files'
    serializer = 'json'
    ignore_result = True

    def run(self, sigids, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        signatures = UserSignature.objects.filter(id__in=sigids)
        if signatures:
            user = signatures[0].user.username
            userid = signatures[0].user.id
            basedir = settings.EMAIL_SIGNATURES_DIR
            logger.info(_("Deleting signatures for: %(a)s") % dict(a=user))
            for sig in signatures:
                if sig.signature_type == 1:
                    sigfile = '%s/users/text/%d.txt' % (basedir, userid)
                if sig.signature_type == 2:
                    sigfile = '%s/users/html/%d.html' % (basedir, userid)
                try:
                    os.unlink(sigfile)
                    sig.delete()
                except os.error, error:
                    logger.info(_("Error deleting %(f)s: %(e)s") %
                                dict(f=sigfile, e=str(error)))
            update_ms_serial(logger)
            logger.info(_("Finished deletion of signatures for: %(u)s") %
                        dict(u=user))
        else:
            logger.info(_('Account signatures not found'))
        