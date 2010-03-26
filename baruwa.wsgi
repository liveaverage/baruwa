import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'baruwa.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
