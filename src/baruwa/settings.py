# Django settings for baruwa project.
# vim: ai ts=4 sts=4 et sw=4

import os
import socket
import djcelery
djcelery.setup_loader()
ugettext = lambda s: s

DEBUG = False
TEMPLATE_DEBUG = DEBUG

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).decode('utf-8')
).replace('\\', '/')

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'
        # or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': '',
        # Not used with sqlite3.
        'USER': '',
        # Not used with sqlite3.
        'PASSWORD': '',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
        'OPTIONS': { 'init_command': 'SET storage_engine=INNODB, SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;' },
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Africa/Johannesburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
  ('en', ugettext('English')),
  ('af', ugettext('Afrikaans')),
  ('it', ugettext('Italian')),
  ('cs', ugettext('Czech')),
  ('fr', ugettext('French')),
  ('pl', ugettext('Polish')),
)

LOCALE_PATHS = (os.path.join(CURRENT_PATH, 'locale'),)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(CURRENT_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'iv1$*mxebib#a=p@+2gs%gp%#hi(61t8!dm((eh$5$-6xl(+0a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'baruwa.utils.context_processors.status',
    'baruwa.utils.context_processors.general',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'baruwa.urls'

TEMPLATE_DIRS = (
    os.path.join(CURRENT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'baruwa.fixups',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'baruwa.auth',
    'baruwa.accounts',
    'baruwa.messages',
    'baruwa.lists',
    'baruwa.reports',
    'baruwa.status',
    'baruwa.config',
    'djcelery',
    'south',
    #'debug_toolbar',
)

AUTHENTICATION_BACKENDS = (
    'baruwa.auth.backends.MailBackend',
    'django.contrib.auth.backends.ModelBackend',
    #'baruwa.auth.radius.RadiusAuth',
)

AUTH_PROFILE_MODULE = 'accounts.userprofile'

INTERNAL_IPS = ('127.0.0.1',)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 28800
#SESSION_COOKIE_SECURE = True
#EMAIL_HOST = 'smtp.example.net'
#DEFAULT_FROM_EMAIL = 'postmaster@baruwa.org'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#celery
CELERY_CONCURRENCY = 20
CELERY_DISABLE_RATE_LIMITS = True
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "baruwa"
BROKER_PASSWORD = "password"
BROKER_VHOST = "baruwa"
CELERY_QUEUES = {
    socket.gethostname(): {
        "exchange_type": "direct",
        "binding_key": socket.gethostname(),
    },
    "default": {
        "exchange": "default",
        "binding_key": "default"
    },
}
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default"

#south
SOUTH_AUTO_FREEZE_APP = True

# Radius auth settings
RADIUS_SECRET = {}
RADIUS_SECRET['127.0.0.1'] = 'secret'

# Baruwa only setting

# location of GeoIP IPv6 DB
GEOIP_IPV6_DB = '/usr/share/GeoIP/GeoIPv6.dat'

# mailscanner configuration file
MS_CONFIG = '/etc/MailScanner/MailScanner.conf'

# mailscanner Quick.Peek program location
MS_QUICKPEEK = '/usr/sbin/Quick.Peek'

# Number of days to keep in the quarantine
QUARANTINE_DAYS_TO_KEEP = 60

# The url to use in your quarantine report links
QUARANTINE_REPORT_HOSTURL = 'http://baruwa-alpha.local'

# spam assassin rules directories
SA_RULES_DIRS = ['/usr/share/spamassassin', '/etc/mail/spamassassin']

# alternative postfix configuration directory
# use this to specify a non default postfix configuration for use
# with the queue monitoring system
#POSTFIX_ALT_CONF = '/etc/postfix-ms'

#load default filter (only display todays messages)
#LOAD_BARUWA_DEFAULT_FILTER = True

#max username length defaults to 255
#MAX_USERNAME_LENGTH = 128

#email signatures base directory
EMAIL_SIGNATURES_DIR = '/etc/MailScanner/signatures'

#number of recent messages to display on front page
# defaults to 50
#BARUWA_NUM_RECENT_MESSAGES = 50

# End Baruwa only settings

try:
    from baruwa.dev_settings import *
except ImportError:
    pass
