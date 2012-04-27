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


from django.conf.urls.defaults import patterns, include, handler500, handler404

urlpatterns = patterns('baruwa.web.reports.views',
    (r'^$', 'index', {}, 'web-reports-index'),
    (r'^(?P<report_kind>(\d+))/$', 'report', {}, 'web-report-kind'),
    (r'^fd/(?P<index_num>(\d+))/$', 'rem_filter', {}, 'web-remove-filter'),
    (r'^fs/(?P<index_num>(\d+))/$', 'save_filter', {}, 'web-save-filter'),
    (r'^sfd/(?P<index_num>(\d+))/$', 'del_filter', {}, 'web-delete-filter'),
    (r'^sfl/(?P<index_num>(\d+))/$', 'load_filter', {}, 'web-load-filter'),
)