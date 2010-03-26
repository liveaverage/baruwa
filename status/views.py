from django.shortcuts import render_to_response
from django.db import connection
from baruwa.reports.views import r_query,raw_user_filter
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

@never_cache
@login_required
def index(request):
    active_filters = []
    c = connection.cursor()
    q = """SELECT COUNT(*) AS mail,SUM(CASE WHEN ((virusinfected=0 OR virusinfected IS NULL) AND (nameinfected=0 OR nameinfected IS NULL)
    AND (otherinfected=0 OR otherinfected IS NULL) AND (isspam=0 OR isspam IS NULL) AND (ishighspam=0 OR ishighspam IS NULL)
    AND (ismcp=0 OR ismcp IS NULL) AND (ishighmcp=0 OR ishighmcp IS NULL)) THEN 1 ELSE 0 end) AS clean_mail,
    SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END) AS virii,
    SUM(CASE WHEN nameinfected>0 AND (virusinfected=0 OR virusinfected IS NULL) AND (otherinfected=0 OR otherinfected IS NULL)
    AND (isspam=0 OR isspam IS NULL) AND (ishighspam=0 OR ishighspam IS NULL) THEN 1 ELSE 0 END) AS infected,
    SUM(CASE WHEN otherinfected>0 AND (nameinfected=0 OR nameinfected IS NULL) AND (virusinfected=0 OR virusinfected IS NULL)
    AND (isspam=0 OR isspam IS NULL) AND (ishighspam=0 OR ishighspam IS NULL) THEN 1 ELSE 0 END) AS otherinfected,
    SUM(CASE WHEN isspam>0 AND (virusinfected=0 OR virusinfected IS NULL) AND (nameinfected=0 OR nameinfected IS NULL)
    AND (otherinfected=0 OR otherinfected IS NULL) AND (ishighspam=0 OR ishighspam IS NULL) THEN 1 ELSE 0 END) AS spam,
    SUM(CASE WHEN ishighspam>0 AND (virusinfected=0 OR virusinfected IS NULL) AND (nameinfected=0 OR nameinfected IS NULL)
    AND (otherinfected=0 OR otherinfected IS NULL) THEN 1 ELSE 0 END) AS highspam,
    SUM(size) AS size FROM maillog WHERE date = CURRENT_DATE()
    """
    if request.user.is_superuser:
        c.execute(q)
    else:
        domains = request.session['user_filter']['domains']
        user_type = request.session['user_filter']['user_type']
        sql = raw_user_filter(request.user,user_type,domains)
        c.execute(q+" AND "+sql)
    row = c.fetchone()
    data = {'total':row[0],'clean':row[1],'virii':row[2],'infected':row[3],'otherinfected':row[4],'spam':row[5],'highspam':row[6]}
    return render_to_response('status/index.html',{'data':data,'user':request.user})
