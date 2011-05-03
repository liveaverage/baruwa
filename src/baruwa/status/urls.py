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

from djcelery import views as celery_views
from django.conf.urls.defaults import patterns, include, handler500, handler404
from django.contrib.auth.decorators import login_required
from baruwa.messages.views import task_status

urlpatterns = patterns('baruwa.status.views',
    (r'^$', 'index', {}, 'status-index'),
    (r'^bayes/$', 'bayes_info', {}, 'bayes-info'),
    (r'^lint/$', 'sa_lint', {}, 'sa-lint'),
    (r'^mailq/$', 'mailq', {'queue': 1}, 'mailq'),
    (r'^mailq/inbound/$', 'mailq', {'queue': 1}, 'mailq-inbound'),
    (r'^mailq/outbound/$', 'mailq', {'queue': 2}, 'mailq-outbound'),
    (r'^mailq/inbound/(?P<order_by>(timestamp|from_address|to_address|subject|size|attempts))/$', 'mailq', {'queue': 1}),
    (r'^mailq/outbound/(?P<order_by>(timestamp|from_address|to_address|subject|size|attempts))/$', 'mailq', {'queue': 2}),
    (r'^mailq/inbound/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|attempts))/$', 'mailq', {'queue': 1}),
    (r'^mailq/outbound/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|attempts))/$', 'mailq', {'queue': 2}),
    (r'^mailq/inbound/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|attempts))/$', 'mailq', {'queue': 1}, 'mailq-inbound-paged'),
    (r'^mailq/outbound/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|attempts))/$', 'mailq', {'queue': 2}, 'mailq-outbound-paged'),
    (r'^mailq/view/(?P<itemid>(([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2})|.+)/$', 'detail', {}, 'mailq-detail'),
    (r'^mailq/process/$', 'delete_from_queue', {}, 'process-mailq'),
    (r'^tasks/json/(?P<task_id>[\w\d\-]+)/$', login_required(celery_views.task_status), {}, 'ajax-task-status'),
    (r'^tasks/(?P<taskid>[\w\d\-]+)/$', task_status, {}, 'task-status'),
)
