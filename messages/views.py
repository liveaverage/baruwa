# vim: ai ts=4 sts=4 et sw=4
from django.shortcuts import render_to_response,get_object_or_404
from messages.models import Maillog
from messages.forms import QuarantineProcessForm
from django.template.loader import render_to_string
from django.utils import simplejson
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.forms.util import ErrorList as errorlist
from django.views.generic.list_detail import object_list
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
#from django.contrib import messages
from messages.process_mail import *
from reports.views import apply_filter
from lists.models import Blacklist,Whitelist

def json_ready(element):
    element['timestamp'] = str(element['timestamp'])
    element['sascore'] = str(element['sascore'])
    return element 

def index(request, list_all=0, page=1, quarantine=0, direction='dsc',order_by='timestamp'):
    active_filters = []
    ordering = order_by
    if direction == 'dsc':
        ordering = order_by
        order_by = "-%s" % order_by

    if not list_all:
        message_list = Maillog.objects.values('id','timestamp','from_address','to_address','subject','size','sascore','ishighspam','isspam'
        ,'virusinfected','otherinfected','spamwhitelisted','spamblacklisted','nameinfected')[:50]
    else:
        if quarantine:
             message_list = Maillog.objects.values('id','timestamp','from_address','to_address','subject','size','sascore','ishighspam','isspam'
            ,'virusinfected','otherinfected','spamwhitelisted','spamblacklisted','quarantined','nameinfected').order_by(order_by).filter(quarantined__exact=1)
        else:
            message_list = Maillog.objects.values('id','timestamp','from_address','to_address','subject','size','sascore','ishighspam','isspam'
            ,'virusinfected','otherinfected','spamwhitelisted','spamblacklisted','nameinfected').order_by(order_by)
        message_list = apply_filter(message_list,request,active_filters)
    if request.is_ajax():
        if not list_all:
            last_id = request.META.get('HTTP_X_LAST_ID', None)
            if last_id != message_list[0]['id']:
                message_list = map(json_ready,message_list)
            else:
                message_list = []
            pg = None
        else:
            p = Paginator(message_list,50)
            if page == 'last':
                page = p.num_pages
            po = p.page(page)
            message_list = po.object_list
            message_list = map(json_ready,message_list)
            page = int(page)
            quarantine = int(quarantine)
            ap = 2
            sp = max(page - ap, 1)
            if sp <= 3: sp = 1
            ep = page + ap + 1
            pn = [n for n in range(sp,ep) if n > 0 and n <= p.num_pages]
            pg = {'page':page,'pages':p.num_pages,'page_numbers':pn,'next':po.next_page_number(),'previous':po.previous_page_number(),
            'has_next':po.has_next(),'has_previous':po.has_previous(),'show_first':1 not in pn,'show_last':p.num_pages not in pn,
            'quarantine':quarantine,'direction':direction,'order_by':ordering}
        json = simplejson.dumps({'items':message_list,'paginator':pg})
        return HttpResponse(json, mimetype='application/javascript')
    else:
        return object_list(request, template_name='messages/index.html', queryset=message_list, paginate_by=50, page=page, 
            extra_context={'quarantine': quarantine,'direction':direction,'order_by':ordering,'app':'messages','active_filters':active_filters,'list_all':list_all})

def detail(request, message_id):
    message_details = get_object_or_404(Maillog, id=message_id)
    quarantine_form = QuarantineProcessForm()
    return render_to_response('messages/detail.html', {'message_details': message_details, 'form': quarantine_form})

def process_quarantined_msg(request):
    html = {}
    learn_as = ""
    form = QuarantineProcessForm(request.POST)
    if form.is_valid():
        id = form.cleaned_data['message_id']
        try:
            m = Maillog.objects.get(pk=id)
        except Maillog.DoesNotExist:
            html = 'the message id does not exist'
            response = simplejson.dumps({'success':'False', 'html': html})
        else:
            success = "True"
            qdir = "/Users/andrew/Downloads"
            date = "%s" % m.date
            date = date.replace('-', '')
            file_name = get_message_path(qdir,date,m.id)
            if not file_name is None:
                if form.cleaned_data['release']:
                    fail=False
                if form.cleaned_data['use_alt']:
                    to_addr = form.cleaned_data['altrecipients']
                else:
                    #to_addr = m.to_address
                    to_addr = "andrew@sentechsa.net"
                    to_addr = to_addr.split(',')
                if not release_mail(file_name,to_addr,m.from_address):
                    fail=True
                    success = "False"
                    template = "messages/released.html"
                    html = render_to_string(template, {'id': m.id,'addrs':to_addr,'failure':fail})
                if form.cleaned_data['salearn']:
                    if int(form.cleaned_data['salearn_as']) == 1:
                        learn_as = "spam"
                        if not m.isspam:
                            m.isfp = 0
                            m.isfn = 1
                        else:
                            m.isfp = 0
                            m.isfn = 0
                    elif int(form.cleaned_data['salearn_as']) == 2:
                        learn_as = "ham"
                        if m.isspam:
                            m.isfp = 1
                            m.isfn = 0
                        else:
                            m.isfp = 0
                            m.isfn = 0
                    elif int(form.cleaned_data['salearn_as']) == 3:
                        learn_as = "forget"
                        m.isfp = 0
                        m.isfn = 0
                    status = sa_learn(file_name, learn_as)
                    template = "messages/salearn.html"
                    if status.success == True:
                        html = render_to_string(template, {'id': m.id,'msg':status.output,'success':status.success})
                        m.save()
                    else:
                        html = render_to_string(template, {'id': m.id,'msg':status.errormsg,'success':status.success})
                if form.cleaned_data['todelete']:
                    import os
                    if os.path.exists(file_name):
                        try:
                            os.remove(file_name)
                        except:
                            pass
                        else:
                            fail=False
                        template = "messages/delete.html"
                        html = render_to_string(template, {'id': m.id,'failure':fail})
            else:
                success = "False"
                html = 'The quarantined file could not be processed'
        response = simplejson.dumps({'success':success, 'html': html})
    else:
        error_list = form.errors.values()[0]
        html = errorlist(error_list).as_ul()
        response = simplejson.dumps({'success':'False','html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

def preview(request, message_id):
    import email
    message = {}
    message_object = get_object_or_404(Maillog, id=message_id)
    #qdir = "/var/spool/MailScanner/quarantine"
    qdir = "/Users/andrew/Downloads"
    date = "%s" % message_object.date
    date = date.replace('-', '')
    file_name = get_message_path(qdir,date,message_id)
    if not file_name is None:
        try:
            fp = open(file_name)
        except:
            raise Http404
        msg = email.message_from_file(fp)
        fp.close()
        message = parse_email(msg)
    return render_to_response('messages/preview.html', {'message':message,'message_id':message_object.id})

def blacklist(request,message_id):
    success = 'True'
    try:
        message = Maillog.objects.get(pk=message_id)
    except Maillog.DoesNotExist:
        html = 'Message with message id %s does not exist' % message_id
        success = 'False'
        pass
    else:
        try:
            bl = Blacklist.objects.get(to_address__iexact=message.to_address,from_address__iexact=message.from_address)
        except Blacklist.DoesNotExist:
            bl = Blacklist(to_address=message.to_address,from_address=message.from_address)
            try:
                bl.save()
            except:
                html = 'An error occured while adding %s to blacklist' % message.from_address
                success = 'False'
                pass
            else:
                html = 'The sender %s has been blacklisted' % message.from_address
        else:
            html = 'The sender %s is already blacklisted' % message.from_address
            success = 'False'
    if request.is_ajax():
        response = simplejson.dumps({'success':success,'html':html})
        return HttpResponse(response,content_type='application/javascript; charset=utf-8')
    else:
        #messages.info(request,html)
        return HttpResponseRedirect(reverse('message-detail', args=[message_id]))

def whitelist(request,message_id):
    success = 'True'
    try:
        message = Maillog.objects.get(pk=message_id)
    except Maillog.DoesNotExist:
        html = 'Message with message id %s does not exist' % message_id
        success = 'False'
        pass
    else:
        try:
            bl = Whitelist.objects.get(to_address__iexact=message.to_address,from_address__iexact=message.from_address)
        except Whitelist.DoesNotExist:
            bl = Whitelist(to_address=message.to_address,from_address=message.from_address)
            try:
                bl.save()
            except:
                html = 'An error occured while adding %s to whitelist' % message.from_address
                success = 'False'
                pass
            else:
                html = 'The sender %s has been whitelisted' % message.from_address
        else:
            html = 'The sender %s is already whitelisted' % message.from_address
            success = 'False'
    if request.is_ajax():
        response = simplejson.dumps({'success':success,'html':html})
        return HttpResponse(response,content_type='application/javascript; charset=utf-8')
    else:
        #messages.info(request,html)
        return HttpResponseRedirect(reverse('message-detail', args=[message_id]))
