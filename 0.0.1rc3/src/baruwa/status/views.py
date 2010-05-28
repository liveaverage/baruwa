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
# vim: ai ts=4 sts=4 et sw=4
from django.shortcuts import render_to_response
from django.db import connection
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.conf import settings
from baruwa.reports.views import gen_dynamic_raw_query, raw_user_filter
from baruwa.messages.process_mail import get_config_option
from baruwa.utilities.decorators import onlysuperusers
import os, subprocess, re

def get_processes(process_name):
    p1 = subprocess.Popen('ps ax',shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen('grep -i '+process_name, shell=True, stdin=p1.stdout,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p3 = subprocess.Popen('grep -v grep',shell=True, stdin=p2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p4 = subprocess.Popen('wc -l',shell=True, stdin=p3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes = p4.stdout.read()
    processes = int(processes.strip())
    return processes


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

    scanners = get_processes('MailScanner')
    ms = get_config_option('MTA')
    mta = get_processes(ms)
    clamd = get_processes('clamd')
    p1 = subprocess.Popen('uptime',shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    u = p1.stdout.read().split()
    uptime = u[2] + ' ' + u[3].rstrip(',')
    data = {'total':row[0],'clean':row[1],'virii':row[2],'infected':row[3],'otherinfected':row[4],'spam':row[5],'highspam':row[6]}
    return render_to_response('status/index.html',{'data':data, 'load':load, 'scanners':scanners, 'mta':mta, 'av':clamd, 'uptime':uptime},
        context_instance=RequestContext(request))

@onlysuperusers
@login_required
def bayes_info(request):
    "Displays bayes database information"

    bayes_info = {}
    regex = re.compile(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+non-token data: (.+)')
    SA_PREFS = getattr(settings, 'SA_PREFS','/etc/MailScanner/spam.assassin.prefs.conf')

    p1 = subprocess.Popen('sa-learn -p '+SA_PREFS+' --dump magic',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    import datetime
    while True:
        line = p1.stdout.readline()
        if not line: break
        m = regex.match(line)
        if m:
            if m.group(5) == 'bayes db version':
                bayes_info['version'] = m.group(3)
            elif m.group(5) == 'nspam':
                bayes_info['spam'] = m.group(3)
            elif m.group(5) == 'nham':
                bayes_info['ham'] = m.group(3)
            elif m.group(5) == 'ntokens':
                bayes_info['tokens'] = m.group(3)
            elif m.group(5) == 'oldest atime':
                bayes_info['otoken'] = datetime.datetime.fromtimestamp(m.group(3))
            elif m.group(5) == 'newest atime':
                bayes_info['ntoken'] = datetime.datetime.fromtimestamp(m.group(3))
            elif m.group(5) == 'last journal sync atime':
                bayes_info['ljournal'] = datetime.datetime.fromtimestamp(m.group(3))
            elif m.group(5) == 'last expiry atime':
                bayes_info['expiry'] = datetime.datetime.fromtimestamp(m.group(3))
            elif m.group(5) == 'last expire reduction count':
                bayes_info['rcount'] = m.group(3)

    return render_to_response('status/bayes.html',{'data':bayes_info},context_instance=RequestContext(request))

@onlysuperusers
@login_required
def sa_lint(request):
    "Displays Spamassassin lint response"

    lint = []
    SA_PREFS = getattr(settings, 'SA_PREFS','/etc/MailScanner/spam.assassin.prefs.conf')

    p1 = subprocess.Popen('spamassassin -x -D -p '+SA_PREFS+' --lint',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = p1.stderr.readline()
        if not line: break
        lint.append(line)

    return render_to_response('status/lint.html',{'data':lint},context_instance=RequestContext(request))
