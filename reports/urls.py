from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.reports.views',
    (r'^$', 'index'),
    (r'^(?P<report_kind>([1-9]{1}|[1]{1}[0-2]{1}))/$', 'report'),
)
