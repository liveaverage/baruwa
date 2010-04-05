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
from setuptools import setup, find_packages
import sys, os, shutil


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='baruwa',
      version="0.0.1b",
      description="Ajax enabled MailScanner web frontend",
      long_description=read('README'),
      keywords='MailScanner Email Filters Quarantine Spam',
      author='Andrew Colin Kissa',
      author_email='andrew@topdog.za.net',
      url='http://www.topdog.za.net/baruwa',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
        'Django>= 1.1.1',
        'MySQLdb>=1.2.1p2',
        'GeoIP',
        'iPy',
      ],
      classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Communications :: Email :: Filters',
                   'Topic :: System :: Monitoring',
                   'Topic :: Multimedia :: Graphics :: Presentation',
                   'Topic :: System :: Systems Administration',
                   ],
      )
