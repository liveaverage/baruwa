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

urlpatterns = patterns('baruwa.messages.views',
    (r'^$', 'index', {}, 'main-messages-index'),
    (r'^(?P<view_type>(full|quarantine|archive))/$', 'index', {'list_all': 1}, 'all-messages-index'),
    (r'^(?P<view_type>(full|quarantine|archive))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$',
    'index', {'list_all': 1}, 'all-messages-list'),
    (r'^(?P<view_type>(full|quarantine|archive))/(?P<page>([0-9]+|last))/$', 'index', {'list_all': 1}, 'all-messages-page'),
    (r'^(?P<view_type>(full|quarantine|archive))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$',
    'index', {'list_all': 1}, 'sorted-messages-page'),
    (r'^(?P<view_type>(full|quarantine|archive))/(?P<quarantine_type>(spam|policyblocked))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$',
    'index', {'list_all': 1}, 'quarantine-messages-list'),
    (r'^(?P<view_type>(quarantine))/(?P<quarantine_type>(spam|policyblocked))/$', 'index', {'list_all': 1}, 'quarantine-bytype-index'),
    (r'^(?P<view_type>(quarantine))/(?P<quarantine_type>(spam|policyblocked))/(?P<page>([0-9]+|last))/$', 'index', {'list_all': 1}, 'quarantine-bytype-pager'),
    (r'^(?P<view_type>(quarantine))/(?P<quarantine_type>(spam|policyblocked))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$'
    , 'index', {'list_all': 1}, 'quarantine-sorted-bytype-pager'),
    (r'^archive/preview/(?P<message_id>([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2}|.+)/$', 'preview',{'archive':True},'archive-preview-message'),
    (r'^preview/(?P<message_id>([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2}|.+)/$', 'preview',{},'preview-message'),
    (r'^dlattachment/(?P<message_id>([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2}|.+)/(?P<attachment_id>(\d+))/$',
    'preview',{'is_attach':True},'download-attachment'),
    (r'^search/$', 'search', {}, 'message-search'),
    (r'^release/(?P<message_uuid>([A-Fa-f0-9]){8}-([A-Fa-f0-9]){4}-([A-Fa-f0-9]){4}-([A-Fa-f0-9]){4}-([A-Fa-f0-9]){12})/$', 'auto_release', {}, 'auto-release'),
    # some message-id's supporting the however using the wildcard regex
    (r'^archive/(?P<message_id>(([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2})|.+)/$', 'detail',{'archive':True},'archive-message-detail'),
    (r'^view/(?P<message_id>(([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2})|.+)/$', 'detail',{},'message-detail'),
)