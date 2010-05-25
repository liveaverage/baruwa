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

import os
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).decode('utf-8')).replace('\\', '/')

urlpatterns = patterns('',
    (r'^$', 'baruwa.messages.views.index', {}, 'index-page'),
    (r'^messages/', include('baruwa.messages.urls')),
    (r'^lists/', include('baruwa.lists.urls')),
    (r'^reports/', include('baruwa.reports.urls')),
    (r'^status/', include('baruwa.status.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root' : os.path.join(CURRENT_PATH, 'static') }),
    (r'^accounts/', include('baruwa.accounts.urls')),
)
