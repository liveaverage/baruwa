from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.reports.views',
    (r'^$', 'index', {}, 'reports-index'),
    (r'^(?P<report_kind>([1-9]{1}|[1]{1}[0-3]{1}))/$', 'report', {}, 'report-kind'),
    (r'^fd/(?P<index_num>(\d+))/$', 'rem_filter', {}, 'remove-filter'),
    (r'^fs/(?P<index_num>(\d+))/$', 'save_filter', {}, 'save-filter'),
    (r'^sfd/(?P<index_num>(\d+))/$', 'del_filter', {}, 'delete-filter'),
    (r'^sfl/(?P<index_num>(\d+))/$', 'load_filter', {}, 'load-filter'),
)
