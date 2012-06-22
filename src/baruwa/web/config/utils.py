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
from django.db import connection

CONFIG_TABLES = ('config_aclrule', 'config_destination',
                'config_destinationcomponent',
                'config_destinationcomponent_destinations',
                'config_destinationpolicy',
                'config_ordereddestination',
                'config_source', 'config_time')

def lock_tables():
    "Lock the configuration tables while verifying or applying"
    conn = connection.cursor()
    sql = """LOCK TABLES %s WRITE, %s WRITE, %s WRITE, %s WRITE,
            %s WRITE, %s WRITE, %s WRITE, %s WRITE""" % CONFIG_TABLES
    conn.execute(sql, [])


def unlock_tables():
    "Unlock configuration tables"
    conn = connection.cursor()
    sql = "UNLOCK TABLES"
    conn.execute(sql, [])
    