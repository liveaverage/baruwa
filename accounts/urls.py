from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$','baruwa.accounts.views.index',{},'accounts'),
    (r'^(?P<page>([0-9]+|last))/$','baruwa.accounts.views.index'),
    (r'^(?P<page>([0-9]+|last)/(?P<direction>(dsc|asc))/(?P<order_by>(username|fullname|type)))/$','baruwa.accounts.views.index'),
    (r'^user/(?P<user_name>(\w+|(\w+@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\.?)|(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\.?))/$','baruwa.accounts.views.user_account'),
    #(r'^login/$','django.contrib.auth.views.login'),
    (r'^login/$','baruwa.accounts.views.login'),
    (r'^logout$','django.contrib.auth.views.logout',{'next_page': '/'},'logout'),
)
