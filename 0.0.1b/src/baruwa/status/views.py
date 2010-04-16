#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from django.shortcuts import render_to_response
from django.db import connection
from baruwa.reports.views import r_query,raw_user_filter
from baruwa.messages.process_mail import get_config_option
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
import os,subprocess

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
        addresses = request.session['user_filter']['filter_addresses']
        user_type = request.session['user_filter']['user_type']
        sql = raw_user_filter(request.user,user_type,addresses)
        c.execute(q+" AND "+sql)
    row = c.fetchone()
    v1, v2, v3 = os.getloadavg()
    load = "%.2f %.2f %.2f" % (v1,v2,v3)
    p1 = subprocess.Popen('ps ax',shell=True,stdout=subprocess.PIPE)
    p2 = subprocess.Popen('grep -i Mailscanner',shell=True,stdin=p1.stdout,stdout=subprocess.PIPE)
    p3 = subprocess.Popen('grep -v grep',shell=True,stdin=p2.stdout,stdout=subprocess.PIPE)
    p4 = subprocess.Popen('wc -l',shell=True,stdin=p2.stdout,stdout=subprocess.PIPE)
    scanners = p4.stdout.read()
    scanners = int(scanners.strip())
    ms = get_config_option('MTA')
    p1 = subprocess.Popen('ps ax',shell=True,stdout=subprocess.PIPE)
    p2 = subprocess.Popen('grep -i '+ms,shell=True,stdin=p1.stdout,stdout=subprocess.PIPE)
    p3 = subprocess.Popen('grep -v grep',shell=True,stdin=p2.stdout,stdout=subprocess.PIPE)
    p4 = subprocess.Popen('wc -l',shell=True,stdin=p2.stdout,stdout=subprocess.PIPE)
    mta = p4.stdout.read()
    mta = int(mta.strip())
    data = {'total':row[0],'clean':row[1],'virii':row[2],'infected':row[3],'otherinfected':row[4],'spam':row[5],'highspam':row[6]}
    return render_to_response('status/index.html',{'data':data,'load':load,'scanners':scanners,'mta':mta,'user':request.user})
