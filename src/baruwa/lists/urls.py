#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.lists.views',
    (r'^$', 'index', {}, 'lists-index'),
    (r'^(?P<list_kind>([1-2]))/$', 'index', {}, 'lists-start'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/$', 'index'),
    (r'^(?P<list_kind>([1-2]))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/$', 'index', {}, 'lists-full-sort'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/$', 'index'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/(?P<search_for>([a-zA-Z_@\.\*]+))/(?P<query_type>(1|2))/$','index'),
    (r'^add/$', 'add_to_list'),
    (r'^delete/(?P<list_kind>([1-2]))/(?P<item_id>(\d+))/$', 'delete_from_list', {}, 'list-del'),
    (r'^delete/$', 'delete_from_list', {}, 'list-delete'),
) 
