import os

os.environ["CELERY_LOADER"] = "django"
os.environ['DJANGO_SETTINGS_MODULE'] = 'baruwa.settings'
os.environ['PYTHON_EGG_CACHE'] = '/var/tmp'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
