#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2012  Andrew Colin Kissa <andrew@topdog.za.net>
# Copyright (C) 2012 Theo Schroeder <t.schroeder@schmolz-bickenbach.com>
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

import ldap
import struct
import logging

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from baruwa.utils.misc import get_exc_str
from baruwa.config.models import MailAuthHost
from baruwa.config.models import MailADAuthHost
from baruwa.accounts.models import UserProfile
from baruwa.accounts.models import UserAddresses

logger = logging.getLogger()
fhandle = logging.FileHandler(settings.AD_LOG_FILE)
fhandle.setLevel(logging.DEBUG)
logger.addHandler(fhandle)


class ADUser(object):

    ldap_connection = None
    ad_search_fields = settings.AD_SEARCH_FIELDS
    ad_ldap_scheme = settings.AD_LDAP_SCHEME

    def get_ldap_url(self):
        """return ldap url"""
	return '%s%s:%s' % (self.ad_ldap_scheme,
                            self.ad_host,
                            self.ad_port)

    def __init__(self, username, host=None, port=None, ad_search_dn=None, ad_admin_group=None, ad_user_group=None, ad_auth_domain=None):
        """initialization"""

        self.username = username
        self.uname = username
        self.ad_host = host if host else settings.AD_HOST_NAME
        self.ad_port = port if port else settings.AD_LDAP_PORT

	# Added for multi-domain authentication with AD parameters stored in auth_domain
	self.ad_search_dn = ad_search_dn if ad_search_dn else settings.AD_SEARCH_DN	
	self.ad_admin_group = ad_admin_group if ad_admin_group else settings.AD_ADMIN_GROUP
	self.ad_user_group = ad_user_group if ad_user_group else settings.AD_USER_GROUP

        try:
	    self.domain = ad_auth_domain if ad_auth_domain else settings.AD_AUTH_DOMAIN
            self.uname = self.username.split('@')[0]
            self.username = self.username.split('@')[0]
            self.user_bind_name = "%s@%s" % (self.username, self.domain)
        except IndexError:
	    self.domain = ad_auth_domain if ad_auth_domain else settings.AD_AUTH_DOMAIN
            self.user_bind_name = "%s@%s" % (self.username, self.domain)

        self.is_bound = False
        self.has_data = False

        self.first_name = None
        self.last_name = None
        self.email = None
        self.is_superuser = False
        self.email_addresses = []

    def connect(self, password):
        """connect to ad"""
        self.password = password
        had_connection = ADUser.ldap_connection is not None
        ret = self._connect(password)
        if not ret and had_connection and ADUser.ldap_connection is None:
            logger.warning("AD reset connection - invalid connection,"
            " try again with new connection")
            ret = self._connect(password)
        return ret

    def _connect(self, password):
        """connect to ad helper"""
        if not password:
            return False
        try:
            if ADUser.ldap_connection is None:
                logger.info("AD auth backend ldap connecting")
                ADUser.ldap_connection = ldap.initialize(self.get_ldap_url())
                assert self.ldap_connection == ADUser.ldap_connection
            self.ldap_connection.simple_bind_s(self.user_bind_name, password)
            self.is_bound = True
        except Exception, exp:
            if str(exp.message).find("connection invalid") >= 0:
                logger.warning("AD reset connection - it "
                "looks like invalid: %s (%s)" % (str(exp), get_exc_str()))
                ADUser.ldap_connection = None
            else:
                logger.error("AD auth backend ldap - "
                "probably bad credentials: %s (%s)" % (str(exp), get_exc_str()))
            return False
        return True

    def disconnect(self):
        """Disconnect AD connection"""
        if self.is_bound:
            logger.info("AD auth backend ldap unbind")
            self.ldap_connection.unbind_s()
            self.is_bound = False

    def sid2str(self, sid):
        srl = ord(sid[0])
        number_sub_id = ord(sid[1])
        iav = struct.unpack('!Q','\x00\x00'+sid[2:8])[0]
        sub_ids = [struct.unpack('<I',sid[8+4*i:12+4*i])[0] for i in range(number_sub_id)]

        return 'S-%d-%d-%s' % (srl, iav, '-'.join([str(s) for s in sub_ids]))

    def check_group(self, obj, group):
        """Check if user is in AD group"""
        found = False

        try:
            assert self.ldap_connection
            res2 = self.ldap_connection.search_ext_s(obj,
                                 ldap.SCOPE_BASE,
                                 "(objectClass=*)",
                                 self.ad_search_fields)

            if not res2:
                return False
            assert len(res2) >= 1, "Result should contain at least one element: %s\n" % res2
            result = res2[0][1]
            if result.has_key('primaryGroupID'):
		pri_grp_rid = result['primaryGroupID'][0]
		domain_sid = self.ldap_connection.search_s(self.ad_search_dn, ldap.SCOPE_BASE)[0][1]['objectSid'][0]
		domain_sid_s = self.sid2str(domain_sid)
		obj_sid = domain_sid_s + '-' + pri_grp_rid
		pri_grp_cn = self.ldap_connection.search_s(self.ad_search_dn, ldap.SCOPE_SUBTREE, "objectSid=%s" % obj_sid, ['cn'])
		if self.check_group (pri_grp_cn[0][0], group):
		    return True
            if result.has_key('sAMAccountName'):
                if result['sAMAccountName'][0] == group:
                    return True
	    if result.has_key('memberOf'):
	        for group2 in result['memberOf']:
                    if self.check_group (group2, group):
                        return True

        except Exception, exp:
            logger.debug("AD auth backend error by fetching"
                        " ldap data: %s (%s)\n" % (str(exp),  get_exc_str()))

        return found

    def get_data(self):
        """Get the user data from AD"""
        try:
            res = self.ldap_connection.search_ext_s(self.ad_search_dn,
                                 ldap.SCOPE_SUBTREE,
                                 "sAMAccountName=%s" % self.uname,
                                 self.ad_search_fields)


            if not res:
                logger.error("b) AD auth ldap backend error by "
                "searching %s. No result.\n" % self.ad_search_dn)
                return False
            assert len(res) >= 1, "c) Result should contain at least one element: %s\n" % res
            result = res[0][1]
        except Exception, exp:
            logger.error("a) Auth failed for (%s)\n" % self.uname )
            logger.error("a) AD auth backend error by fetching"
                        " ldap data: %s (%s)\n" % (str(exp), get_exc_str()))
            return False

        try:
            self.first_name = None
            if result.has_key('givenName'):
                self.first_name = result['givenName'][0]

            self.last_name = None
            if result.has_key('sn'):
                self.last_name = result['sn'][0]

            self.email = None
            if result.has_key('mail'):
                self.email = result['mail'][0]

            if result.has_key('proxyAddresses'):
                for mail1 in result['proxyAddresses']:
                    if mail1.split(':')[0].upper() == "SMTP":
                        self.email_addresses.append(mail1.split(':')[1])
                        logger.error("Adding Address: %s\n", mail1)

            basedn = res[0][0]

            if self.check_group(basedn, self.ad_admin_group):
                self.is_superuser = True
            elif self.check_group(basedn, self.ad_user_group):
                self.is_superuser = False
            else:
                logger.error("User %s not in group", self.username)
                return False
            self.has_data = True
        except Exception, exp:
            logger.error("AD auth backend error by reading"
            " fetched data: %s (%s)\n" % (str(exp),  get_exc_str()))
            return False

        return True

    def __del__(self):
        "Disconnect"
        try:
            self.disconnect()
        except Exception, exp:
            logger.error("AD auth backend error when "
            "disconnecting: %s (%s)\n" % (str(exp),  get_exc_str()))
            return False

    def __str__(self):
        "String representation"
        return "AdUser(<%s>, connected=%s, is_bound=%s, has_data=%s)\n" % (
            self.username, self.ldap_connection is not None,
            self.is_bound,
            self.has_data)

class ActiveDirectoryBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        """Authenticate to the AD backends"""
        if not '@' in username:
            logger.warning("Domain not specified for %s\n" % username)
            return None

        _, domain = username.split('@')

        dom = UserAddresses.objects.filter(address=domain, address_type=1)
        if not dom:
            logger.warning("AD auth not enabled for %s\n" % domain)
            return None

        hosts = MailAuthHost.objects.filter(useraddress=dom,
                                            protocol=5,
                                            enabled=True)

        if not hosts:
            logger.warning("No AD servers found for %s\n" % domain)
            return None

	adset = None

        for host in hosts:
            # process all hosts
	
            # Query each host for configured AD settings:
            try:
                adset = MailADAuthHost.objects.get(ad_host=host)
                aduser = ADUser(username, host.address, host.port, adset.ad_search_dn, adset.ad_admin_group, adset.ad_user_group, adset.ad_auth_domain)
            except MailADAuthHost.DoesNotExist:
                logger.warning("No MySQL MailADAuthHost; using setting.py AD config\n")
                aduser = ADUser(username, host.address, host.port, adset, adset, adset, adset)

            if not aduser.connect(password):
                logger.warning("AD bind failed for %s\n" % username)
                continue

            user = None

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                logger.warning("User missing %s. creating\n" % username)
                user = User(username=username,
                            is_staff = False,
                            is_superuser = False)
                user.set_unusable_password()

            if not aduser.get_data():
                logger.warning("AD auth backend failed when reading data for"
                " %s. No Group information available." % username)
                user = None
                continue
            else:
                do_update = False
                for attr in ['first_name',
                            'last_name',
                            'email',
                            'is_superuser']:
                    if not getattr(user, attr) == getattr(aduser, attr):
                        setattr(user, attr, getattr(aduser, attr))
                        do_update = True
                if do_update:
                    user.save()

                if not user.is_superuser:
                    for mail1 in aduser.email_addresses:
                        try:
                            address = UserAddresses.objects.get(user=user,
                                        address=mail1)
                        except UserAddresses.DoesNotExist:
                            address = UserAddresses(user=user,
                                                    address=mail1)
                            address.save()

            logger.info("AD auth backend check passed for %s" % username)
            if user:
                try:
                    profile = user.get_profile()
                except UserProfile.DoesNotExist:
                    account_type = 3
                    if user.is_superuser:
                        account_type = 1
                    profile = UserProfile(user=user,
                                        account_type=account_type)
                    profile.save()
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
