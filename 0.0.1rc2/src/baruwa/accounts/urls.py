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

urlpatterns = patterns('',
    (r'^$','baruwa.accounts.views.index',{},'accounts'),
    (r'^(?P<page>([0-9]+|last))/$','baruwa.accounts.views.index'),
    (r'^(?P<page>([0-9]+|last)/(?P<direction>(dsc|asc))/(?P<order_by>(username|fullname|type)))/$','baruwa.accounts.views.index'),
    (r'^user/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.user_account',{},'user-profile'),
    (r'^user/account/$', 'baruwa.accounts.views.user_account',{},'user-account'),
    (r'^user/(?P<user_id>([0-9]+))/add-filter/$', 'baruwa.accounts.views.user_account',{'add_filter':True},'add-filter'),
    (r'^user/(?P<user_id>([0-9]+))/process-filter/$', 'baruwa.accounts.views.add_filter',{},'process-filter'),
    (r'^user/delete/filter/(?P<user_id>([0-9]+))/(?P<filter>([0-9]+))/$', 'baruwa.accounts.views.delete_filter',{},'delete-filter'),
    (r'^user/delete/filter/$', 'baruwa.accounts.views.delete_filter',{},'rdelete-filter'),
    (r'^login/$','baruwa.accounts.views.login'),
    (r'^logout$','django.contrib.auth.views.logout',{'next_page': '/'},'logout'),
)
