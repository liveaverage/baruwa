from django.conf.urls.defaults import *

urlpatterns = patterns('status.views',
    (r'^$', 'index'),
)
