from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.messages.views',
    (r'^$', 'index'),
    (r'^full/$', 'index', {'list_all': 1}),
    (r'^full/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$', 
    'index', {'list_all': 1}),
    (r'^full/(?P<page>([0-9]+|last))/$', 'index', {'list_all': 1}),
    (r'^full/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$',
    'index', {'list_all': 1}),
    (r'^quarantine/$', 'index', {'list_all': 1,'quarantine': 1}),
    (r'^quarantine/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$', 
    'index', {'list_all': 1,'quarantine': 1}),
    (r'^quarantine/(?P<page>([0-9]+|last))/$', 'index', {'list_all': 1,'quarantine': 1}),
    (r'^quarantine/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(timestamp|from_address|to_address|subject|size|sascore))/$'
    , 'index', {'list_all': 1,'quarantine': 1}),
    (r'^(?P<message_id>([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2})/$', 'detail'),
    (r'^preview/(?P<message_id>([A-Za-z0-9]){6}-([A-Za-z0-9]){6}-([A-Za-z0-9]){2})/$', 'preview'),
    (r'^process_quarantine/$', 'process_quarantined_msg'),
)
