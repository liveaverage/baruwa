# 
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# vim: ai ts=4 sts=4 et sw=4
#

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db import connection
from django.conf import settings
from baruwa.utils.misc import raw_user_filter, get_processes, get_config_option
from baruwa.utils.decorators import onlysuperusers
import os, subprocess, re


@login_required
def index(request):
    active_filters = []
    c = connection.cursor()
    import datetime

    
    today = datetime.date.today()
    q = """SELECT COUNT(*) AS mail, SUM(CASE WHEN virusinfected=0 AND nameinfected=0
    AND otherinfected=0 AND spam=0 AND highspam=0 THEN 1 ELSE 0 END) AS clean_mail,
    SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END) AS virii,
    SUM(CASE WHEN nameinfected>0 AND virusinfected=0 AND otherinfected=0
    AND spam=0 AND highspam=0 THEN 1 ELSE 0 END) AS infected,
    SUM(CASE WHEN otherinfected>0 AND nameinfected=0 AND virusinfected=0
    AND spam=0 AND highspam=0 THEN 1 ELSE 0 END) AS otherinfected,
    SUM(CASE WHEN spam>0 AND virusinfected=0 AND nameinfected=0
    AND otherinfected=0 AND highspam=0 THEN 1 ELSE 0 END) AS spam_mail,
    SUM(CASE WHEN highspam>0 AND virusinfected=0 AND nameinfected=0
    AND otherinfected=0 THEN 1 ELSE 0 END) AS high_spam,
    SUM(size) AS size FROM messages WHERE date = '%s'
    """ % today
    if request.user.is_superuser:
        c.execute(q)
    else:
        sql = raw_user_filter(request)
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
    data = {'total':row[0],'clean':row[1],'virii':row[2],'infected':row[3],'otherinfected':row[4],
        'spam':row[5],'highspam':row[6]}
    return render_to_response('status/index.html',{'data':data, 'load':load, 'scanners':scanners,
        'mta':mta, 'av':clamd, 'uptime':uptime}, context_instance=RequestContext(request))
        
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
                bayes_info['otoken'] = datetime.datetime.fromtimestamp(float(m.group(3)))
            elif m.group(5) == 'newest atime':
                bayes_info['ntoken'] = datetime.datetime.fromtimestamp(float(m.group(3)))
            elif m.group(5) == 'last journal sync atime':
                bayes_info['ljournal'] = datetime.datetime.fromtimestamp(float(m.group(3)))
            elif m.group(5) == 'last expiry atime':
                bayes_info['expiry'] = datetime.datetime.fromtimestamp(float(m.group(3)))
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
