import sys
import site
import os

# Python virtualenv path
vepath = '/home/andrew/py24/lib/python2.4/site-packages'
# Path to Baruwa package installed in the virtualenv
fullpath = '/home/andrew/py24/lib/python2.4/site-packages/baruwa-1.1.0-py2.4.egg/baruwa'

prev_sys_path = list(sys.path)
site.addsitedir(vepath)
sys.path.append(fullpath)
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

from django.core.handlers.wsgi import WSGIHandler
os.environ["CELERY_LOADER"] = "django"
os.environ['DJANGO_SETTINGS_MODULE'] = 'baruwa.settings'
os.environ['PYTHON_EGG_CACHE'] = '/var/tmp'
application = WSGIHandler()