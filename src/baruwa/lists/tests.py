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

import httplib

from django.test import TestCase, Client
from django.core import urlresolvers
from django.contrib.auth.models import User


class ListsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('andrew',
        'andrew@topdog.za.net', 'password')
        self.user.is_superuser = True
        self.user.save()

    def test_unauth_access(self):
        page = urlresolvers.reverse('lists-index')
        response = self.client.get(page)
        self.failUnless(response)
        self.assertRedirects(response,
        urlresolvers.reverse('please-login') + '?next=' + page)

    def test_whitelists(self):
        page = urlresolvers.reverse('lists-start', args=[1])
        self.client.login(username='andrew', password='password')
        response = self.client.get(page)
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

    def test_blacklists(self):
        page = urlresolvers.reverse('lists-start', args=[2])
        self.client.login(username='andrew', password='password')
        response = self.client.get(page)
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

    def test_add_to_list(self):
        page = urlresolvers.reverse('add-to-list')
        self.client.login(username='andrew', password='password')
        response = self.client.post(page, {'from_address': '192.168.1.0/24',
        'user_part': '', 'to_address': '', 'list_type': 2},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnless(response)
        self.assertEqual(response.content, '{"error_msg": "", "success": true}')

    def test_delete_from_list(self):
        page = urlresolvers.reverse('add-to-list')
        self.client.login(username='andrew', password='password')
        self.client.post(page, {'from_address': '192.168.1.0/24',
        'user_part': '', 'to_address': '', 'list_type': 2},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        page = urlresolvers.reverse('list-del', args=[1])
        response = self.client.post(page, {'list_item': 1},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnless(response)
        self.assertEqual(response.content, '{"success": true}')
