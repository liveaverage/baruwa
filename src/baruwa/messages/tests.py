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


class MessagesTestCase(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user('andrew',
        'andrew@topdog.za.net', 'password')
        self.user.is_superuser = True
        self.user.save()

    def test_view_homepage(self):
        homepage = urlresolvers.reverse('index-page')
        response = self.client.get(homepage)
        self.failUnless(response)
        self.assertRedirects(response,
        urlresolvers.reverse('please-login') + '?next=/')

    def test_loggedin_view_homepage(self):
        homepage = urlresolvers.reverse('index-page')
        self.client.login(username='andrew', password='password')
        response = self.client.get(homepage)
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

    def test_ajax_homepage(self):
        homepage = urlresolvers.reverse('index-page')
        self.client.login(username='andrew', password='password')
        response = self.client.get(homepage, {},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

    def test_view_full_listing(self):
        page = urlresolvers.reverse('all-messages-index', args=['full'])
        self.client.login(username='andrew', password='password')
        response = self.client.get(page)
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

    def test_view_quarantine(self):
        page = urlresolvers.reverse('all-messages-index', args=['quarantine'])
        self.client.login(username='andrew', password='password')
        response = self.client.get(page)
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

    def test_view_archive(self):
        page = urlresolvers.reverse('all-messages-index', args=['archive'])
        self.client.login(username='andrew', password='password')
        response = self.client.get(page)
        self.failUnless(response)
        self.assertEqual(response.status_code, httplib.OK)

