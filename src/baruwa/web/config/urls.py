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


from django.conf.urls.defaults import patterns, include, handler500,\
handler404

urlpatterns = patterns('baruwa.web.config.views',
    (r'^$', 'index', {}, 'main-settings-index'),
    (r'^acls/$', 'acls', {}, 'acl-rules'),
    (r'^acls/(?P<page>([0-9]+|last))/$', 'acls', {}, 'acls-rules-paged'),
    (r'^acls/add/$', 'add_acl', {}, 'add-acl-rule'),
    (r'^acls/edit/(?P<aclid>(\d+))/$', 'edit_acl', {},
    'edit-acl-rule'),
    (r'^acls/delete/(?P<aclid>(\d+))/$', 'delete_acl', {},
    'delete-acl-rule'),
    (r'^acls/move/(?P<direction>(up|down))/(?P<aclid>(\d+))/$', 'move_acl', {},
    'move-acl-rule'),
    (r'^times/$', 'times', {}, 'time-rules'),
    (r'^times/(?P<page>([0-9]+|last))/$', 'times', {},
    'time-rules-paged'),
    (r'^times/add/$', 'add_time', {}, 'add-time-rule'),
    (r'^times/edit/(?P<tid>(\d+))/$', 'edit_time', {},
    'edit-time-rule'),
    (r'^times/delete/(?P<tid>(\d+))/$', 'delete_time', {},
    'delete-time-rule'),
    (r'^sources/$', 'sources', {}, 'source-rules'),
    (r'^sources/(?P<page>([0-9]+|last))/$', 'sources', {},
    'source-rules-paged'),
    (r'^sources/add/$', 'add_source', {}, 'add-source-rule'),
    (r'^sources/edit/(?P<sid>(\d+))/$', 'edit_source', {},
    'edit-source-rule'),
    (r'^sources/delete/(?P<sid>(\d+))/$', 'delete_source', {},
    'delete-source-rule'),
    (r'^dcs/$', 'destination_component', {}, 'dc-rules'),
    (r'^dcs/(?P<page>(\d+|last))/$', 'destination_component', {},
    'dc-rules-paged'),
    (r'^dcs/add/$', 'add_dc', {}, 'add-dc-rule'),
    (r'^dcs/edit/(?P<dcid>(\d+))/$', 'edit_dc', {}, 'edit-dc-rule'),
    (r'^dcs/delete/(?P<dcid>(\d+))/$', 'delete_dc', {}, 'delete-dc-rule'),
    (r'^destinations/$', 'destinations', {}, 'destination-rules'),
    (r'^destinations/(?P<page>(\d+|last))/$', 'destination_component', {},
    'destination-rules-paged'),
    (r'^destinations/add/$', 'add_destination', {}, 'add-destination-rule'),
    (r'^destinations/edit/(?P<did>(\d+))/$', 'edit_destination', {},
    'edit-destination-rule'),
    (r'^destinations/delete/(?P<did>(\d+))/$', 'delete_destination', {},
    'delete-destination-rule'),
    (r'^ods/$', 'ordered_destinations', {}, 'od-rules'),
    (r'^ods/(?P<page>(\d+|last))/$', 'ordered_destinations', {},
    'ods-rules-paged'),
    (r'^ods/add/$', 'add_ods', {}, 'add-ods-rule'),
    (r'^ods/edit/(?P<odid>(\d+))/$', 'edit_ods', {}, 'edit-ods-rule'),
    (r'^ods/delete/(?P<odid>(\d+))/$', 'delete_ods', {}, 'delete-ods-rule'),
    (r'^ods/move/(?P<direction>(up|down))/(?P<odid>(\d+))/$', 'move_od', {},
    'move-od-rule'),
    (r'^dps/$', 'destination_policy', {}, 'dps-rules'),
    (r'^dps/(?P<page>(\d+|last))/$', 'destination_policy', {},
    'dps-rules-paged'),
    (r'^dps/add/$', 'add_dps', {}, 'add-dps-rule'),
    (r'^dps/edit/(?P<dpid>(\d+))/$', 'edit_dps', {}, 'edit-dps-rule'),
    (r'^dps/delete/(?P<dpid>(\d+))/$', 'delete_dps', {}, 'delete-dps-rule'),
    (r'^verify/$', 'verify_config', {}, 'verify-config'),
    (r'^apply/$', 'apply_config', {}, 'apply-config'),
)