from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.status.views',
    (r'^$', 'index'),
)
