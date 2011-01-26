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

import re, urllib

from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.translation import ugettext as _
from baruwa.messages.models import Message, Release, Archive
from baruwa.messages.forms import QuarantineProcessForm
from baruwa.utils.process_mail import search_quarantine, host_is_local
from baruwa.utils.process_mail import release_mail, remote_release
from baruwa.utils.process_mail import remote_attachment_download, \
remote_preview, remote_process, sa_learn
from baruwa.utils.misc import jsonify_msg_list, apply_filter, jsonify_status
from baruwa.utils.mail.message import EmailParser
from baruwa.utils.context_processors import status

@login_required
def index(request, list_all=0, page=1, view_type='full', direction='dsc',
        order_by='timestamp', quarantine_type=None):
    """index"""
    active_filters = []
    ordering = order_by
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
            'scaned').filter(timestamp__gt=last_ts)[:50]
        else:
            message_list = Message.messages.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'nameinfected',
            'scaned')[:50]
    else:
        if view_type == 'archive':
            message_list = Archive.messages.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'nameinfected',
            'scaned').order_by(order_by)
        elif view_type == 'quarantine':
            message_list = Message.quarantine.for_user(request).values(
            'id', 'timestamp', 'from_address', 'to_address', 'subject',
            'size', 'sascore', 'highspam', 'spam', 'virusinfected',
            'otherinfected', 'whitelisted', 'blacklisted', 'isquarantined',
            'nameinfected', 'scaned').order_by(order_by)
            if quarantine_type == 'spam':
                message_list = message_list.filter(spam=1)
            if quarantine_type == 'policyblocked':
                message_list = message_list.filter(spam=0) 
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
            p = Paginator(message_list, 50)
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
            pg = {'page':page, 'pages':p.num_pages, 'page_numbers':pn,
            'next':po.next_page_number(), 'previous':po.previous_page_number(),
            'has_next':po.has_next(), 'has_previous':po.has_previous(),
            'show_first':1 not in pn, 'show_last':p.num_pages not in pn,
            'view_type':view_type, 'direction':direction, 'order_by':ordering,
            'quarantine_type':quarantine_type}
        json = simplejson.dumps({'items':message_list, 'paginator':pg, 
                                'status':sys_status})
        return HttpResponse(json, mimetype='application/javascript')

    if list_all:
        return object_list(request, template_name='messages/index.html',
        queryset=message_list, paginate_by=50, page=page,
        extra_context={'view_type': view_type, 'direction': direction,
        'order_by': ordering, 'active_filters':active_filters,
        'list_all':list_all, 'quarantine_type': quarantine_type},
        allow_empty=True)
    else:
        return object_list(request, template_name='messages/index.html',
        queryset=message_list, extra_context={'view_type':view_type,
        'direction':direction, 'order_by':ordering,
        'active_filters':active_filters, 'list_all':list_all,
        'quarantine_type':quarantine_type})

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
        return HttpResponseForbidden(
            _('You are not authorized to access this page'))

    error_list = ''
    quarantine_form = QuarantineProcessForm()
    quarantine_form.fields[
    'message_id'].widget.attrs['value'] = message_details.id

    if request.method == 'POST':
        quarantine_form = QuarantineProcessForm(request.POST)
        success = True
        if quarantine_form.is_valid():
            if not host_is_local(message_details.hostname):
                params = urllib.urlencode(request.POST)
                remote_response = remote_process(message_details.hostname,
                    request.META['HTTP_COOKIE'], message_id, params)
                response = remote_response['response']
                if request.is_ajax():
                    return HttpResponse(response,
                        content_type='application/javascript; charset=utf-8')
                try:
                    resp = simplejson.loads(response)
                    if resp['success']:
                        success = True
                    else:
                        success = False
                    error_list = resp['response']
                except:
                    success = False
                    error_list = _('Error: Empty server response')
            else:
                file_name = search_quarantine(message_details.date, message_id)
                if not file_name is None:
                    if quarantine_form.cleaned_data['release']:
                        # release
                        if quarantine_form.cleaned_data['use_alt']:
                            to_addr = quarantine_form.cleaned_data[
                            'altrecipients']
                        else:
                            to_addr = message_details.to_address
                        to_addr = to_addr.split(',')
                        if not release_mail(file_name, to_addr,
                            message_details.from_address):
                            success = False
                        template = 'messages/released.html'
                        html = render_to_string(template, 
                            {'id': message_details.id, 'addrs':to_addr, 
                            'success':success})
                    if quarantine_form.cleaned_data['salearn']:
                        #salean
                        salearn_opts = ('spam', 'ham', 'forget')
                        template = "messages/salearn.html"
                        salearn = int(
                                    quarantine_form.cleaned_data['salearn_as'])
                        salearn = salearn - 1 
                        if salearn <= 2:
                            status = sa_learn(file_name, salearn_opts[salearn])
                            if not status['success']:
                                success = False
                            html = render_to_string(template,
                                {'id': message_details.id,
                                'msg':status['output'], 'success':success})
                        else:
                            success = False
                            html = _('Invalid salearn options supplied')
                    if quarantine_form.cleaned_data['todelete']:
                        #delete
                        import os
                        if os.path.exists(file_name):
                            try:
                                os.remove(file_name)
                                message_details.quarantined = 0
                                message_details.save()
                            except:
                                success = False
                        template = "messages/delete.html"
                        html = render_to_string(template,
                            {'id': message_details.id, 'success':success})
                else:
                    html = _('The quarantined file could not be processed')
                    success = False
        else:
            error_list = quarantine_form.errors.values()[0]
            error_list = error_list[0]
            html = error_list
            success = False
        if request.is_ajax():
            response = simplejson.dumps({'success':success, 'html': html})
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

    if host_is_local(message_details.hostname):
        file_name = search_quarantine(message_details.date, message_id)
        if not file_name is None:
            try:
                import email
                fip = open(file_name, 'r')
                msg = email.message_from_file(fip)
                fip.close()
                email_parser = EmailParser()
                if is_attach:
                    message = email_parser.get_attachment(msg, attachment_id)
                    if message:
                        import base64
                        attachment_data = message.getvalue()
                        mimetype = message.content_type
                        if request.is_ajax():
                            json = simplejson.dumps({'success':True,
                            'attachment':base64.encodestring(attachment_data),
                            'mimetype':mimetype, 'name':message.name})
                            response = HttpResponse(json,
                            content_type='application/javascript; charset=utf-8')
                            message.close()
                            return response
                        response = HttpResponse(
                            attachment_data, mimetype=mimetype)
                        response['Content-Disposition'] = (
                            'attachment; filename=%s' % message.name)
                        message.close()
                        return response
                    else:
                        raise Http404
                else:
                    message = email_parser.parse_msg(msg)
                if request.is_ajax():
                    response = simplejson.dumps({'message':message,
                        'message_id':message_details.id})
                    return HttpResponse(response,
                        content_type='application/javascript; charset=utf-8')
                return render_to_response('messages/preview.html', 
                    {'message':message, 'message_id':message_details.id},
                 context_instance=RequestContext(request))
            except:
                raise Http404
        else:
            raise Http404
    else:
        #remote
        if is_attach:
            remote_response = remote_attachment_download(
                message_details.hostname, request.META['HTTP_COOKIE'], 
                message_id, attachment_id, archive)
            if remote_response['success']:
                import base64
                data = remote_response['response']
                attach = simplejson.loads(data)
                if attach['success']:
                    attachment_data = base64.decodestring(attach['attachment'])
                    mimetype = attach['mimetype']
                    response = HttpResponse(attachment_data, mimetype=mimetype)
                    response['Content-Disposition'] = (
                        'attachment; filename=%s' % attach['name'])
                    return response
            raise Http404
        else:
            remote_response = remote_preview(message_details.hostname,
                request.META['HTTP_COOKIE'], message_id, archive)
            if remote_response['success']:
                data = remote_response['response']
                items = simplejson.loads(data)
                message = items['message']

                if request.is_ajax():
                    response = simplejson.dumps({'message':message,
                        'message_id':message_id})
                    return HttpResponse(response,
                        content_type='application/javascript; charset=utf-8')
                else:
                    return render_to_response('messages/preview.html',
                        {'message':message, 'message_id':message_id},
                        context_instance=RequestContext(request))
            else:
                raise Http404

@login_required
def search(request):
    "Redirect to message details"
    if (request.method == 'POST') and request.REQUEST['message_id']:
        message_details = get_object_or_404(Message, 
                                    id=request.REQUEST['message_id'])
        return HttpResponseRedirect(reverse('message-detail',
            args=[message_details.id]))
    return HttpResponseRedirect(reverse('main-index'))

def auto_release(request, message_uuid, template='messages/release.html'):
    "Releases message from the quarantine without need to login"

    success = False

    release_record = get_object_or_404(Release, uuid=message_uuid, released=0)
    message_details = get_object_or_404(Message, id=release_record.message_id)

    if not host_is_local(message_details.hostname):
        remote_response = remote_release(message_details.hostname,
            release_record.uuid)
        response = remote_response['response']
        if request.is_ajax():
            return HttpResponse(response,
                content_type='application/javascript; charset=utf-8')
        try:
            json_response = simplejson.loads(response)
            if json_response['success']:
                success = True
                release_record.released = 1
                release_record.save()
        except:
            pass
    else:
        file_name = search_quarantine(message_details.date,
            release_record.message_id)
        if not file_name is None:
            if release_mail(file_name, message_details.to_address,
                message_details.from_address):
                success = True
                release_record.released = 1
                release_record.save()
        else:
            raise Http404

    html = render_to_string('messages/released.html',
        {'id': message_details.id, 'addrs':message_details.to_address,
        'success':success})

    if request.is_ajax():
        response = simplejson.dumps({'success':success, 'html': html})
        return HttpResponse(response,
            content_type='application/javascript; charset=utf-8')
    return render_to_response(template,
        {'message_id':release_record.message_id,
        'release_address':message_details.to_address, 'success':success},
        context_instance=RequestContext(request))
