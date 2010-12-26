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
import os

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).decode('utf-8')).replace('\\', '/')

js_info_dict = {
    'packages': ('baruwa',),
}

urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^$', 'baruwa.messages.views.index', {}, 'index-page'),
    (r'^messages/', include('baruwa.messages.urls')),
    (r'^lists/', include('baruwa.lists.urls')),
    (r'^reports/', include('baruwa.reports.urls')),
    (r'^status/', include('baruwa.status.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : os.path.join(CURRENT_PATH, 'static') }),
    (r'^accounts/', include('baruwa.accounts.urls')),
    (r'^settings/', include('baruwa.config.urls')),
)
