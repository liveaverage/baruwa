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

import datetime

from django.conf import settings
from django.db.models import Count

from baruwa.web.visits.models import Traffic


def web_totals(request):
    "web totals"

    web_totals_interval = getattr(settings, 'BARUWA_WEB_TOTALS_INTERVAL', 5)
    interval = datetime.timedelta(minutes=web_totals_interval)
    last_date = datetime.datetime.today() - interval
    totals = Traffic.objects\
                    .filter(date__gte=last_date.date())\
                    .filter(time__gte=last_date.time())\
                    .aggregate(web_users=Count('authuser'), web_hosts=Count('ip'))
    return totals
    
    