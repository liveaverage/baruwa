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
#

from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.config.views',
    (r'^$', 'index', {}, 'settings-index'),
    (r'^(?P<page>([0-9]+|last))/$','index'),
    (r'^(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|address))/$', 'index', {}, 'domains-list'), 
    (r'^domains/(?P<domain_id>([0-9]+))/$', 'view_domain', {}, 'view-domain'),
    (r'^domains/(?P<domain_id>([0-9]+))/addhost/$', 'add_host', {}, 'add-host'),
    (r'^domains/(?P<domain_id>([0-9]+))/add/authhost/$', 'add_auth_host', {}, 'add-auth-host'),
    (r'^hosts/(?P<host_id>([0-9]+))/delete/$', 'delete_host', {}, 'delete-host'),
    (r'^hosts/(?P<host_id>([0-9]+))/edit/$', 'edit_host', {}, 'edit-host'),
    (r'^hosts/(?P<host_id>([0-9]+))/test/$', 'test_host', {}, 'test-host'),
    (r'^auth/(?P<host_id>([0-9]+))/edit/$', 'edit_auth_host', {}, 'edit-auth-host'),
    (r'^auth/(?P<host_id>([0-9]+))/delete/$', 'delete_auth_host', {}, 'delete-auth-host'),
    (r'^scanners/$', 'list_scanners', {}, 'list-scanners'),
    (r'^scanners/(?P<page>([0-9]+|last))/$','list_scanners'),
    (r'^scanners/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|address))/$', 'list_scanners'),
    (r'^scanners/view/(?P<scanner_id>([0-9]+))/$', 'view_scanner', {}, 'view-scanner'),
    (r'^scanners/init/(?P<scanner_id>([0-9]+))/$', 'init_scanner', {}, 'init-scanner'),
    (r'^scanners/(?P<scanner_id>([0-9]+))/settings/(?P<section_id>([0-9]+))/$', 'view_settings', {}, 'view-section'),
)