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

from django.conf import settings

from baruwa.utils.misc import get_sys_status


def status(request):
    "Set status variables"

    status = {'baruwa_status': '', 'baruwa_mail_total': '',
            'baruwa_spam_total': '', 'baruwa_virus_total': ''}

    if not hasattr(request, 'user'):
        return status

    if not request.user.is_authenticated():
        return status

    if request.is_ajax() and not request.path.startswith('/messages/'):
        return status

    status = get_sys_status(request)

    return status

def general(request):
    "set misc variables"
    num_of_recent_msgs = getattr(settings, 'BARUWA_NUM_RECENT_MESSAGES', 50)
    return {'baruwa_num_recent_messages': num_of_recent_msgs}
