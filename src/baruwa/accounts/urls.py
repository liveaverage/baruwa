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

urlpatterns = patterns('',
    (r'^$','baruwa.accounts.views.index', {}, 'accounts'), 
    (r'^(?P<page>([0-9]+|last))/$','baruwa.accounts.views.index'),
    (r'^(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|username|fullname|type))/$','baruwa.accounts.views.index'),
    (r'^user/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.user_profile',{},'user-profile'),
    (r'^user/update/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.update_account', {}, 'update-account'),
    (r'^user/pw/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.change_password', {}, 'change-pw'),
    (r'^user/delete/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.delete_account', {}, 'delete-account'),
    (r'^create/$', 'baruwa.accounts.views.create_account', {}, 'create-account'),
    (r'^profile/$', 'baruwa.accounts.views.profile', {}, 'user-account'),
    (r'^profile/update/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.update_profiles', {}, 'update-profile'),
    (r'^add/address/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.add_address', {}, 'add-address'),
    (r'^add/domain/(?P<user_id>([0-9]+))/$', 'baruwa.accounts.views.add_address', {'is_domain':True}, 'add-domain'),
    (r'^edit/address/(?P<address_id>([0-9]+))/$', 'baruwa.accounts.views.edit_address', {}, 'edit-address'),
    (r'^delete/address/(?P<address_id>([0-9]+))/$', 'baruwa.accounts.views.delete_address', {}, 'delete-address'),
    (r'^login/$','baruwa.accounts.views.local_login', {}, 'please-login'),
    (r'^logout$','django.contrib.auth.views.logout',{'next_page': '/'},'logout'),
    (r'^pwchange/$', 'django.contrib.auth.views.password_change', 
    {'template_name': 'accounts/change_pw.html', 'post_change_redirect': '/accounts/profile/'}, 'change-password'),
)