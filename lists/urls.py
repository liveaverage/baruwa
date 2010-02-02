from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.lists.views',
    (r'^$', 'index'),
    (r'^add/$', 'add_to_list'),
    (r'^delete/(?P<list_kind>([1-2]))/(?P<item_id>(\d+))/$', 'delete_from_list'),
) 
