
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *

import os
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).decode('utf-8')).replace('\\', '/')

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'baruwa.messages.views.index'),
    (r'^messages/', include('baruwa.messages.urls')),
    (r'^lists/', include('baruwa.lists.urls')),
    (r'^reports/', include('baruwa.reports.urls')),
    (r'^status/', include('baruwa.status.urls')),
    (r'^tools/', include('baruwa.tools.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root' : os.path.join(CURRENT_PATH, 'static') }),
    (r'^accounts/', include('baruwa.accounts.urls')),
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
