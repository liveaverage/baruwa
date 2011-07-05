#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2011  Andrew Colin Kissa <andrew@topdog.za.net>
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

import os
import re
import datetime
import subprocess

from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib import messages as djmessages

from baruwa.utils.misc import get_processes, get_config_option
from baruwa.utils.decorators import onlysuperusers
from baruwa.messages.models import MessageStats
from baruwa.status.models import MailQueueItem
from baruwa.status.forms import DeleteQueueItems


@login_required
def index(request):
    "displays the status"
    addrs = []
    act = 3

    inq = MailQueueItem.objects.filter(direction=1)
    outq = MailQueueItem.objects.filter(direction=2)

    if not request.user.is_superuser:
        addrs = request.session['user_filter']['addresses']
        act = request.session['user_filter']['account_type']
        if act == 2:
            query = Q()
            for addr in addrs:
                atdomain = "@%s" % addr
                query = query | Q(Q(**{'from_address__iendswith': atdomain}) |
                                Q(**{'to_address__iendswith': atdomain}))
            inq = inq.filter(query)
            outq = outq.filter(query)
        if act == 3:
            inq = inq.filter(Q(from_address__in=addrs) |
                                Q(to_address__in=addrs))
            outq = outq.filter(Q(from_address__in=addrs) |
                                Q(to_address__in=addrs))

    data = MessageStats.objects.get(request.user, addrs, act)
    inq = inq.aggregate(count=Count('messageid'))
    outq = outq.aggregate(count=Count('messageid'))

    val1, val2, val3 = os.getloadavg()
    load = "%.2f %.2f %.2f" % (val1, val2, val3)

    scanners = get_processes('MailScanner')
    mas = get_config_option('MTA')
    mta = get_processes(mas)
    clamd = get_processes('clamd')

    pipe1 = subprocess.Popen(['uptime'], stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
    upt = pipe1.communicate()[0].split()
    uptime = upt[2] + ' ' + upt[3].rstrip(',')

    return render_to_response('status/index.html', {'data': data, 'load': load,
        'scanners': scanners, 'mta': mta, 'av': clamd, 'uptime': uptime,
        'outq': outq['count'], 'inq': inq['count']},
        context_instance=RequestContext(request))


@onlysuperusers
@login_required
def bayes_info(request):
    "Displays bayes database information"

    info = {}
    regex = re.compile(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+non-token data: (.+)')
    sa_prefs = getattr(settings, 'SA_PREFS',
        '/etc/MailScanner/spam.assassin.prefs.conf')

    pipe1 = subprocess.Popen(['sa-learn', '-p', sa_prefs, '--dump', 'magic'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = pipe1.stdout.readline()
        if not line:
            break
        match = regex.match(line)
        if match:
            if match.group(5) == 'bayes db version':
                info['version'] = match.group(3)
            elif match.group(5) == 'nspam':
                info['spam'] = match.group(3)
            elif match.group(5) == 'nham':
                info['ham'] = match.group(3)
            elif match.group(5) == 'ntokens':
                info['tokens'] = match.group(3)
            elif match.group(5) == 'oldest atime':
                info['otoken'] = datetime.datetime.fromtimestamp(
                    float(match.group(3)))
            elif match.group(5) == 'newest atime':
                info['ntoken'] = datetime.datetime.fromtimestamp(
                float(match.group(3)))
            elif match.group(5) == 'last journal sync atime':
                info['ljournal'] = datetime.datetime.fromtimestamp(
                float(match.group(3)))
            elif match.group(5) == 'last expiry atime':
                info['expiry'] = datetime.datetime.fromtimestamp(
                float(match.group(3)))
            elif match.group(5) == 'last expire reduction count':
                info['rcount'] = match.group(3)

    return render_to_response('status/bayes.html', {'data': info},
        context_instance=RequestContext(request))


@onlysuperusers
@login_required
def sa_lint(request):
    "Displays Spamassassin lint response"

    lint = []
    sa_prefs = getattr(
        settings, 'SA_PREFS', '/etc/MailScanner/spam.assassin.prefs.conf')

    pipe1 = subprocess.Popen(['spamassassin', '-x', '-D', '-p', sa_prefs,
    '--lint'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = pipe1.stderr.readline()
        if not line:
            break
        lint.append(line)

    return render_to_response('status/lint.html', {'data': lint},
        context_instance=RequestContext(request))


@login_required
def mailq(request, queue, page=1, direction='dsc', order_by='timestamp'):
    "Display the items in the mailq"
    items = MailQueueItem.objects.filter(direction=queue)

    if not request.user.is_superuser:
        addrs = request.session['user_filter']['addresses']
        act = request.session['user_filter']['account_type']
        if act == 2:
            query = Q()
            for addr in addrs:
                atdomain = "@%s" % addr
                query = query | Q(Q(**{'from_address__iendswith': atdomain}) |
                                Q(**{'to_address__iendswith': atdomain}))
            items = items.filter(query)
        if act == 3:
            items = items.filter(Q(from_address__in=addrs) |
                                Q(to_address__in=addrs))

    ordering = order_by
    if direction == 'dsc':
        ordering = order_by
        order_by = '-%s' % order_by

    items = items.order_by(order_by)
    if queue == 1:
        urlstring = 'mailq-inbound'
    else:
        urlstring = 'mailq-outbound'
    app = reverse(urlstring)
    form = DeleteQueueItems()
    choices = [(item.id, item.id) for item in items[:50]]
    form.fields['queueid']._choices = choices
    form.fields['queueid'].widget.choices = choices
    request.session['queue_choices'] = choices
    request.session.modified = True

    return object_list(request, template_name='status/mailq.html',
    queryset=items, paginate_by=50, page=page,
    extra_context={'list_all': True, 'app': app.strip('/'),
    'direction': direction, 'order_by': ordering, 'form': form},
    allow_empty=True)


@login_required
def detail(request, itemid):
    "show queued mail details"
    itemdetails = get_object_or_404(MailQueueItem, id=itemid)
    return render_to_response('status/detail.html',
    {'itemdetails': itemdetails}, context_instance=RequestContext(request))


@login_required
def delete_from_queue(request):
    "delete queue items"
    sendto = reverse('mailq')
    if request.method == 'POST':
        form = DeleteQueueItems(request.POST)
        choices = request.session['queue_choices']
        form.fields['queueid']._choices = choices
        if form.is_valid():
            queueids = form.cleaned_data['queueid']
            MailQueueItem.objects.filter(id__in=queueids).update(flag=1)
            msg = _("The queue items (%(num)d) have "
            "been flagged for deletion") % {'num': len(queueids)}
            request.session['queue_choices'] = []
            request.session.modified = True
        else:
            msg = _("The queue items could not be processed")
        djmessages.info(request, msg)
        referer = request.META.get('HTTP_REFERER', None)
        if referer and '/mailq' in referer:
            sendto = referer
    return HttpResponseRedirect(sendto)
