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
from django.conf.urls.defaults import *
from piston.resource import Resource
from baruwa.api.handlers import MessageProcess,MessagePreview
from piston.authentication import HttpBasicAuthentication

auth = HttpBasicAuthentication(realm="My Realm")
ad = { 'authentication': auth }

#messages_handler = Resource(handler=MessagesHandler)
process_handler = Resource(handler=MessageProcess)
preview_handler = Resource(handler=MessagePreview)

urlpatterns = patterns('',
    url(r'^messages/process_quarantine/$',process_handler),
    url(r'^preview/(?P<message_id>([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2})/$',preview_handler),
)
