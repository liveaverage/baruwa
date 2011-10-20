import os
import sys

from setuptools import setup, find_packages


install_requires = ['setuptools',
    'Django>= 1.2',
    'django-celery',
    'reportlab',
    'anyjson',
    'iPy',
    'lxml',
    'South',
]

if sys.version_info < (2, 5):
    install_requires.append('uuid')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='baruwa',
      version="1.1.1",
      description="Ajax enabled MailScanner web frontend",
      long_description=read('README'),
      keywords='MailScanner Email Filters Quarantine Spam',
      author='Andrew Colin Kissa',
      author_email='andrew@topdog.za.net',
      url='http://www.baruwa.org',
      license='GPL',
      platforms=["any"],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      scripts=['bin/baruwa-admin',
                'bin/baruwa-syslog'],
      include_package_data=True,
      zip_safe=False,
      dependency_links=[],
      install_requires=install_requires,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Telecommunications Industry',
            'Intended Audience :: Customer Service',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Operating System :: POSIX :: BSD',
            'Operating System :: POSIX :: SunOS/Solaris',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Communications :: Email :: Filters',
            'Topic :: System :: Monitoring',
            'Topic :: Multimedia :: Graphics :: Presentation',
            'Topic :: System :: Systems Administration', ],
      )
