from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.lists.views',
    (r'^$', 'index', {}, 'lists-index'),
    (r'^(?P<list_kind>([1-2]))/$', 'index', {}, 'lists-start'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/$', 'index'),
    (r'^(?P<list_kind>([1-2]))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/$', 'index', {}, 'lists-full-sort'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/$', 'index'),
    (r'^(?P<list_kind>([1-2]))/(?P<page>([0-9]+|last))/(?P<direction>(dsc|asc))/(?P<order_by>(id|to_address|from_address))/(?P<search_for>([a-zA-Z_@\.\*]+))/(?P<query_type>(1|2))/$','index'),
    (r'^add/$', 'add_to_list', {}, 'add-to-list'),
    (r'^delete/(?P<item_id>(\d+))/$', 'delete_from_list', {}, 'list-del'),
) 
