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

urlpatterns = patterns('baruwa.reports.views',
    (r'^$', 'index'),
    #(r'^(?P<report_type>(s|r))/(?P<report_field>(e|d))/(?P<report_order>(q|v))/$','report'),
    #(r'^(?P<report_type>(a))/(?P<report_field>(h|m|v))/$','report',{'report_order':None}),
    #(r'^(?P<report_type>(p))/$','report',{'report_field':None,'report_order':None}),
    (r'^(?P<report_kind>([1-9]{1}|[1]{1}[0-3]{1}))/$', 'report'),
    (r'^fd/(?P<index_num>(\d+))/$', 'rem_filter'),
    (r'^fs/(?P<index_num>(\d+))/$', 'save_filter'),
    (r'^sfd/(?P<index_num>(\d+))/$', 'del_filter'),
    (r'^sfl/(?P<index_num>(\d+))/$', 'load_filter'),
)
