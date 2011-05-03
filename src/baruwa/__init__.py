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

"""
Baruwa (swahili for letter or mail) is a web 2.0 MailScanner front-end.

It provides an easy to use interface for managing a MailScanner installation.
It is used to perform operations such as releasing quarantined messages,
spam learning, whitelisting and blacklisting addresses, monitoring the health
of the services etc.

Baruwa is implemented using web 2.0 features (AJAX) where deemed fit, graphing
is also implemented on the client side using SVG, Silverlight or VML.
Baruwa has full support for i18n, letting you support any language of your
choosing.

It includes reporting functionality with an easy to use query builder, results
can be displayed as message lists or graphed as colorful and pretty interactive
graphs.

Custom MailScanner modules are provided to allow for logging of messages to the
mysql database with SQLite as backup, managing whitelists and blacklists and
managing per user spam check settings.

Baruwa is open source software, written in Python/Perl using the Django
Framework and MySQL for storage, it is released under the GPLv2 and is
available for free download.

"""

__author__ = "Andrew Colin Kissa"
__copyright__ = "Copyright 2010-2011 Andrew Colin Kissa"
__license__ = "GPLv2"
__email__ = "andrew@topdog.za.net"
__version__ = "1.1.0"
