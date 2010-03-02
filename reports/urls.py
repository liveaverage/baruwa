from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    (r'^$', 'index'),
    #(r'^(?P<report_type>(s|r))/(?P<report_field>(e|d))/(?P<report_order>(q|v))/$','report'),
    #(r'^(?P<report_type>(a))/(?P<report_field>(h|m|v))/$','report',{'report_order':None}),
    #(r'^(?P<report_type>(p))/$','report',{'report_field':None,'report_order':None}),
    (r'^(?P<report_kind>([1-9]{1}|[1]{1}[0-3]{1}))/$', 'report'),
    (r'^fd/(?P<index>(\d+))/$', 'rem_filter'),
    (r'^fs/(?P<index>(\d+))/$', 'save_filter'),
    (r'^sfd/(?P<index>(\d+))/$', 'del_filter'),
    (r'^sfl/(?P<index>(\d+))/$', 'load_filter'),
)
