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

from StringIO import StringIO

from django.core.validators import email_re
from django.contrib.auth.models import User
from django.conf import settings
from baruwa.accounts.models import UserProfile
from baruwa.config.models import MailAuthHost
from baruwa.accounts.models import UserAddresses


DICTIONARY = u"""
ATTRIBUTE User-Name     1 string
ATTRIBUTE User-Password 2 string encrypt=1
"""


class RadiusAuth:
    """Authenticate to a RADIUS server"""
    supports_anonymous_user = False
    supports_object_permissions = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        try:
            from pyrad import packet
            from pyrad.client import Client, Timeout
            from pyrad.dictionary import Dictionary
        except ImportError:
            return None

        if not '@' in username:
            return None

        username = username.decode('utf-8')
        password = password.decode('utf-8')
        login_user, domain = username.split('@')
        dom = UserAddresses.objects.filter(address=domain, address_type=1)

        if not dom:
            return None

        hosts = MailAuthHost.objects.filter(useraddress=dom, protocol=3)

        if not hosts:
            return None

        for host in hosts:
            if not host.split_address:
                login_user = username

            try:
                client = Client(server=host.address,
                                authport=host.port,
                                secret=settings.RADIUS_SECRET[host.address].encode('utf-8'),
                                dict=Dictionary(StringIO(DICTIONARY)),)
            except AttributeError:
                return None

            request = client.CreateAuthPacket(code=packet.Accessrequest,
                User_Name=login_user,)
            request["User-Password"] = request.PwCrypt(password)
            try:
                reply = client.SendPacket(request)
                if (reply.code == packet.AccessReject or
                    reply.code != packet.AccessAccept):
                    return None
            except (Timeout, Exception):
                return None
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.set_unusable_password()
                user.is_staff = False
                user.is_superuser = False
                if email_re.match(username):
                    user.email = username
                user.save()
            try:
                profile = user.get_profile()
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=user, account_type=3)
                profile.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
