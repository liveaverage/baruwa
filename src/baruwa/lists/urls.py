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

from django.conf.urls.defaults import patterns, include, handler500, handler404

urlpatterns = patterns('baruwa.lists.views',
    (r'^$', 'index', {}, 'lists-index'),
    (r'^(?P<list_kind>([1-2]))/$', 'index', {}, 'lists-start'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/$', 'index'),
    (r'^(?P<list_kind>([1-2]))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/$', 'index', {}, 'lists-full-sort'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/$', 'index'),
    (r'^add/$', 'add_to_list', {}, 'add-to-list'),
    (r'^delete/(?P<item_id>(\d+))/$', 'delete_from_list', {}, 'list-del'),
    (r'^rmfilter/$', 'rem_filter', {}, 'rem-filter'),
)
