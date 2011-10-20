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

import re
import base64
import anyjson

from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages as djmessages
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.translation import ugettext as _
from celery.task.sets import TaskSet
from celery.result import TaskSetResult

from baruwa.messages.models import Message, Release, Archive, DeliveryInfo
from baruwa.messages.tasks import ProcessQuarantine, PreviewMessageTask,\
 ReleaseMessage, ProcessQuarantinedMsg
from baruwa.messages.forms import QuarantineProcessForm, BulkQuarantineProcessForm
from baruwa.utils.misc import jsonify_msg_list, jsonify_status
from baruwa.utils.queryfilters import apply_filter
from baruwa.utils.context_processors import status


@login_required
def index(request, list_all=0, page=1, view_type='full', direction='dsc',
        order_by='timestamp', quarantine_type=None):
    """index"""
    active_filters = []
    ordering = order_by
    form = None
    num_of_recent_msgs = getattr(settings, 'BARUWA_NUM_RECENT_MESSAGES', 50)
    template_name = 'messages/index.html'
    if direction == 'dsc':
        ordering = order_by
        order_by = '-%s' % order_by

    if not list_all:
        last_ts = request.META.get('HTTP_X_LAST_TIMESTAMP', None)
        if not last_ts is None:
            last_ts = last_ts.strip()
            if not re.match(
                r'^(\d{4})\-(\d{2})\-(\d{2})(\s)(\d{2})\:(\d{2})\:(\d{2})$',
                last_ts):
                last_ts = None
        if not last_ts is None and request.is_ajax():
            message_list = Message.messages.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'nameinfected',
            'scaned').filter(timestamp__gt=last_ts)[:num_of_recent_msgs]
        else:
            message_list = Message.messages.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'nameinfected',
            'scaned')[:num_of_recent_msgs]
    else:
        if view_type == 'archive':
            message_list = Archive.messages.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'nameinfected',
            'scaned').order_by(order_by)
        elif view_type == 'quarantine':
            template_name = 'messages/quarantine.html'
            message_list = Message.quarantine.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'isquarantined',
            'nameinfected', 'scaned').order_by(order_by)
            if quarantine_type == 'spam':
                message_list = message_list.filter(spam=1)
            if quarantine_type == 'policyblocked':
                message_list = message_list.filter(spam=0)
            form = BulkQuarantineProcessForm()
            form.fields['altrecipients'].widget.attrs['size'] = '55'
            message_list = apply_filter(message_list, request, active_filters)
            p = Paginator(message_list, num_of_recent_msgs)
            if page == 'last':
                page = p.num_pages
            po = p.page(page)
            choices = [(message['id'], message['id']) for message in po.object_list]
            form.fields['message_id']._choices = choices
            form.fields['message_id'].widget.choices = choices
            request.session['quarantine_choices'] = choices
            request.session.modified = True
        else:
            message_list = Message.messages.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'nameinfected',
            'scaned').order_by(order_by)
        message_list = apply_filter(message_list, request, active_filters)
    if request.is_ajax():
        sys_status = jsonify_status(status(request))
        if not list_all:
            message_list = map(jsonify_msg_list, message_list)
            pg = None
        else:
            p = Paginator(message_list, num_of_recent_msgs)
            if page == 'last':
                page = p.num_pages
            po = p.page(page)
            message_list = po.object_list
            message_list = map(jsonify_msg_list, message_list)
            page = int(page)
            ap = 2
            startp = max(page - ap, 1)
            if startp <= 3:
                startp = 1
            endp = page + ap + 1
            pn = [n for n in range(startp, endp) if n > 0 and n <= p.num_pages]
            pg = {'page': page, 'pages': p.num_pages, 'page_numbers': pn,
            'next': po.next_page_number(), 'previous': po.previous_page_number(),
            'has_next': po.has_next(), 'has_previous': po.has_previous(),
            'show_first': 1 not in pn, 'show_last': p.num_pages not in pn,
            'view_type': view_type, 'direction': direction, 'order_by': ordering,
            'quarantine_type': quarantine_type}
        json = anyjson.dumps({'items': message_list, 'paginator': pg,
                                'status': sys_status})
        return HttpResponse(json, mimetype='application/javascript')

    if list_all:
        return object_list(request, template_name=template_name,
        queryset=message_list, paginate_by=num_of_recent_msgs, page=page,
        extra_context={'view_type': view_type, 'direction': direction,
        'order_by': ordering, 'active_filters': active_filters,
        'list_all': list_all, 'quarantine_type': quarantine_type,
        'quarantine_form': form},
        allow_empty=True)
    else:
        return object_list(request, template_name=template_name,
        queryset=message_list, extra_context={'view_type': view_type,
        'direction': direction, 'order_by': ordering,
        'active_filters': active_filters, 'list_all': list_all,
        'quarantine_type': quarantine_type})


@login_required
def detail(request, message_id, archive=False):
    """
    Displays details of a message, and processes quarantined messages
    """
    if archive:
        obj = Archive
    else:
        obj = Message
    message_details = get_object_or_404(obj, id=message_id)
    if not message_details.can_access(request):
        return HttpResponseForbidden(_('You are not authorized'
        ' to access this page'))

    delivery_reports = DeliveryInfo.objects.filter(id=message_id)
    error_list = ''
    quarantine_form = QuarantineProcessForm()
    quarantine_form.fields[
    'message_id'].widget.attrs['value'] = message_details.id

    if request.method == 'POST':
        quarantine_form = QuarantineProcessForm(request.POST)
        if quarantine_form.is_valid():
            form_data = quarantine_form.cleaned_data
            form_data['message_id'] = [form_data['message_id']]
            task = ProcessQuarantine.apply_async(args=[form_data],
            queue=message_details.hostname)
            html = []
            task.wait()
            result = task.result[0]
            if task.status == 'SUCCESS':
                success = True
                if form_data['release']:
                    #release
                    if form_data['use_alt']:
                        to_addr = form_data['altrecipients']
                    else:
                        to_addr = message_details.to_address
                    to_addr = to_addr.split(',')
                    error_msg = ''
                    if not result['release']:
                        success = False
                        error_msg = dict(result['errors'])['release']
                    template = 'messages/released.html'
                    html.append(render_to_string(template,
                        {'id': message_details.id, 'addrs': to_addr,
                        'success': success, 'error_msg': error_msg}))
                if form_data['learn']:
                    #salean
                    error_msg = ''
                    template = "messages/salearn.html"
                    if not result['learn']:
                        success = False
                        error_msg = dict(result['errors'])['learn']
                    html.append(render_to_string(template,
                        {'id': message_details.id, 'msg': error_msg,
                        'success': success}))
                if form_data['todelete']:
                    #delete
                    error_msg = ''
                    if not result['delete']:
                        success = False
                        error_msg = dict(result['errors'])['delete']
                    template = "messages/delete.html"
                    html.append(render_to_string(template,
                    {'id': message_details.id, 'success': success,
                    'error_msg': error_msg}))
                html = '<br />'.join(html)
            else:
                success = False
                html = _('Processing the request failed')
        else:
            error_list = quarantine_form.errors.values()[0]
            error_list = error_list[0]
            html = error_list
            success = False
        if request.is_ajax():
            response = anyjson.dumps({'success': success, 'html': html})
            return HttpResponse(response,
            content_type='application/javascript; charset=utf-8')

    quarantine_form.fields['altrecipients'].widget.attrs['size'] = '55'
    return render_to_response('messages/detail.html', locals(),
        context_instance=RequestContext(request))


@login_required
def preview(request, message_id, is_attach=False, attachment_id=0,
        archive=False):
    """
    Returns a message preview of a quarantined message, depending on
    the call it returns XHTML or JSON
    """
    if archive:
        obj = Archive
    else:
        obj = Message
    message_details = get_object_or_404(obj, id=message_id)
    if not message_details.can_access(request):
        return HttpResponseForbidden(
            _('You are not authorized to access this page'))
    if is_attach:
        preview_task = PreviewMessageTask.apply_async(args=[message_id,
        str(message_details.date), attachment_id],
        queue=message_details.hostname)
        preview_task.wait()
        if preview_task.result:
            result = preview_task.result
            response = HttpResponse(base64.decodestring(result['attachment']),
            mimetype=result['mimetype'])
            response['Content-Disposition'] = (
            'attachment; filename=%s' % result['name'])
            return response
        msg = _("The requested attachment could not be downloaded")
    else:
        preview_task = PreviewMessageTask.apply_async(args=[message_id,
        str(message_details.date)], queue=message_details.hostname)
        preview_task.wait()
        if preview_task.result:
            result = preview_task.result
            return render_to_response('messages/preview.html',
            {'message': result, 'message_id': message_id},
            context_instance=RequestContext(request))
        msg = _("The requested message could not be previewed")
    djmessages.info(request, msg)
    return HttpResponseRedirect(reverse('message-detail',
    args=[message_id]))


@login_required
def search(request):
    "Redirect to message details"
    if (request.method == 'POST') and request.REQUEST['message_id']:
        message_details = get_object_or_404(Message,
                                    id=request.REQUEST['message_id'])
        return HttpResponseRedirect(reverse('message-detail',
            args=[message_details.id]))
    msg = _("No messages found with that message id")
    djmessages.info(request, msg)
    return HttpResponseRedirect(reverse('main-messages-index'))


def auto_release(request, message_uuid, template='messages/release.html'):
    "Releases message from the quarantine without need to login"
    release_record = get_object_or_404(Release, uuid=message_uuid, released=0)
    message_details = get_object_or_404(Message, id=release_record.message_id)
    task = ReleaseMessage.apply_async(args=[message_details.id,
    str(message_details.date), message_details.from_address,
    message_details.to_address.split(',')], queue=message_details.hostname)
    task.wait()
    if task.status == 'SUCCESS':
        result = task.result
    else:
        result = {'success': False, 'error': 'Processing of message failed'}
    return render_to_response(template,
    {'message_id': release_record.message_id,
    'release_address': message_details.to_address,
    'success': result['success'], 'error_msg': result['error']},
    context_instance=RequestContext(request))


@login_required
def bulk_process(request):
    "Process a bulk form"
    if request.method == 'POST':
        form = BulkQuarantineProcessForm(request.POST)
        choices = request.session['quarantine_choices']
        form.fields['message_id']._choices = choices
        if form.is_valid():
            messages = Message.objects.values('id', 'from_address', 'date',
            'hostname', 'to_address').filter(id__in=form.cleaned_data['message_id'])
            del form.cleaned_data['message_id']
            formvals = []
            for message in messages:
                message.update(form.cleaned_data)
                message['date'] = str(message['date'])
                message['message_id'] = message['id']
                del message['id']
                formvals.append(message)
            taskset = TaskSet(tasks=[ProcessQuarantinedMsg.subtask(
            args=[formval], options=dict(queue=formval['hostname']))
            for formval in formvals])
            task = taskset.apply_async()
            task.save()
            return HttpResponseRedirect(reverse('task-status',
            args=[task.taskset_id]))

    msg = _('System was unable to process your request')
    djmessages.info(request, msg)
    return HttpResponseRedirect(reverse('all-messages-index',
    args=['quarantine']))


@login_required
def task_status(request, taskid):
    """
    Return task status based on:
    djcelery.views.task_status
    """
    result = TaskSetResult.restore(taskid)
    percent = "0.0"
    status = 'PROGRESS'
    results = []
    if result.ready():
        finished = True
        results = result.join()
    else:
        finished = False
        percent = "%.1f" % ((1.0 * int(result.completed_count()) / int(result.total)) * 100)
    rdict = {'taskid': taskid, 'finished': finished, 'results': results,
    'status': status, 'completed': percent}
    if request.is_ajax():
        response = anyjson.dumps(rdict)
        return HttpResponse(response,
        content_type='application/javascript; charset=utf-8')
    return render_to_response('messages/task_status.html', rdict,
    context_instance=RequestContext(request))
