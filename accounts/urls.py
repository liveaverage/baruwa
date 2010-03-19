from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$','accounts.views.index',{},'accounts'),
    (r'^(?P<page>([0-9]+|last))/$','accounts.views.index'),
    (r'^(?P<page>([0-9]+|last)/(?P<direction>(dsc|asc))/(?P<order_by>(username|fullname|type)))/$','accounts.views.index'),
    (r'^login/$','django.contrib.auth.views.login'),
    (r'^logout$','django.contrib.auth.views.logout',{'next_page': '/'},'logout'),
)
