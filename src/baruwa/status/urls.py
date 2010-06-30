from django.conf.urls.defaults import *

urlpatterns = patterns('baruwa.status.views',
    (r'^$', 'index', {}, 'status-index'),
    (r'^bayes/$','bayes_info',{},'bayes-info'),
    (r'^lint/$','sa_lint',{},'sa-lint'),
)