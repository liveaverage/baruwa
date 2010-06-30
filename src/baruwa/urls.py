from django.conf.urls.defaults import *
import os

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).decode('utf-8')).replace('\\', '/')

urlpatterns = patterns('',
    (r'^$', 'baruwa.messages.views.index', {}, 'index-page'),
    (r'^messages/', include('baruwa.messages.urls')),
    (r'^lists/', include('baruwa.lists.urls')),
    (r'^reports/', include('baruwa.reports.urls')),
    (r'^status/', include('baruwa.status.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : os.path.join(CURRENT_PATH, 'static') }),
    (r'^accounts/', include('baruwa.accounts.urls')),
)
