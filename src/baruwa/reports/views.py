from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.db.models import Count, Max, Min
from django.db import IntegrityError, connection
from django.utils import simplejson
from django.contrib import messages
from django.forms.util import ErrorList as errorlist
from django.template.defaultfilters import force_escape
from baruwa.reports.forms import FilterForm, FILTER_ITEMS, FILTER_BY
from baruwa.reports.models import SavedFilter
from baruwa.reports.utils import to_dict, pack_json_data, run_query, run_hosts_query, \
format_sa_data, format_totals_data, gen_dynamic_raw_query 
from baruwa.messages.models import Message
from baruwa.utils.misc import gen_dynamic_query, raw_user_filter

@login_required
def index(request):
    """index"""
    errors = ''
    success = True
    active_filters = []
    data = Message.messages.for_user(request)
    saved_filters = []
    filters = SavedFilter.objects.all().filter(user=request.user)
    filter_form = FilterForm()
    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            cleaned_data = filter_form.cleaned_data
            in_field = force_escape(cleaned_data['filtered_field'])
            in_value = force_escape(cleaned_data['filtered_value'])
            in_filtered_by = int(cleaned_data['filtered_by'])
            if not request.session.get('filter_by', False):
                request.session['filter_by'] = []
                request.session['filter_by'].append({'field':in_field, 'filter':in_filtered_by, 'value':in_value})
            else:
                fitem = {'field':in_field, 'filter':in_filtered_by, 'value':in_value}
                if not fitem in request.session['filter_by']:
                    request.session['filter_by'].append(fitem)
                    request.session.modified = True
                else:
                    success = False
                    errors = "The requested filter is already being used"
            filter_list = request.session.get('filter_by')
            data = gen_dynamic_query(data, filter_list, active_filters)
        else:
            success = False
            error_list = filter_form.errors.values()[0]
            errors = error_list[0] #errorlist(error_list).as_ul()
            if request.session.get('filter_by', False):
                filter_list = request.session.get('filter_by')
                data = gen_dynamic_query(data, filter_list, active_filters)
    else:
        filter_form = FilterForm()
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            data = gen_dynamic_query(data, filter_list, active_filters)

    data = data.aggregate(count=Count('timestamp'), newest=Max('timestamp'), oldest=Min('timestamp'))
    if filters.count() > 0:
        filter_items = to_dict(list(FILTER_ITEMS))
        filter_by = to_dict(list(FILTER_BY))
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
        else:
            filter_list = []
        for filter in filters:
            loaded = 0
            if filter_list:
                loaded = 0
                for fitem in filter_list:
                    if fitem['filter'] == filter.op_field and fitem['value'] == filter.value and fitem['field'] == filter.field:
                        loaded = 1
                        break
            saved_filters.append({'filter_id':filter.id, 'filter_name':force_escape(filter.name), 'is_loaded':loaded})
            
    if request.is_ajax():
        if not data['newest'] is None and not data['oldest'] is None:
            data['newest'] = data['newest'].strftime("%a %d %b %Y @ %H:%M %p")
            data['oldest'] = data['oldest'].strftime("%a %d %b %Y @ %H:%M %p")
        else:
            data['newest'] = ''
            data['oldest'] = ''
        response = simplejson.dumps({'success':success,'data':data,'errors':errors,
            'active_filters':active_filters,'saved_filters':saved_filters})
        return HttpResponse(response, content_type='application/javascript; charset=utf-8')
       
    return render_to_response('reports/index.html', {'form':filter_form, 
        'data':data, 'errors':errors, 'active_filters':active_filters, 
        'saved_filters':saved_filters}, context_instance=RequestContext(request))
    
@login_required
def rem_filter(request, index_num):
    if request.session.get('filter_by', False):
        li = request.session.get('filter_by')
        li.remove(li[int(index_num)])
        request.session.modified = True
        if request.is_ajax():
            return index(request)
        msg = 'The filter has been removed.'
        messages.error(request, msg) 
    return HttpResponseRedirect(reverse('reports-index'))
    

@login_required
def save_filter(request, index_num):
    error_msg = ''
    if request.session.get('filter_by', False):
        filter_items = to_dict(list(FILTER_ITEMS))
        filter_by = to_dict(list(FILTER_BY))

        filters = request.session.get('filter_by')
        filter = filters[int(index_num)]
        name = filter_items[filter["field"]]+" "+filter_by[int(filter["filter"])]+" "+filter["value"]
        f = SavedFilter(name=name, field=filter["field"], op_field=filter["filter"], value=filter["value"], user=request.user)
        try:
            f.save()
            msg = 'The filter has been saved.'
            messages.error(request, msg) 
        except IntegrityError:
            error_msg = 'This filter already exists'
            messages.error(request, error_msg)
        if request.is_ajax():
            if error_msg == '':
                return index(request)
            else:
                response = simplejson.dumps({'success':False,'data':[],'errors':error_msg,'active_filters':[],'saved_filters':[]})
                return HttpResponse(response, content_type='application/javascript; charset=utf-8')
    return HttpResponseRedirect(reverse('reports-index'))
    
@login_required
def load_filter(request, index_num):
    try:
        filter = SavedFilter.objects.get(id=int(index_num))
        if not request.session.get('filter_by', False):
            request.session['filter_by'] = []
            request.session['filter_by'].append({'field':filter.field,'filter':filter.op_field,'value':filter.value})
        else:
            fitem = {'field':filter.field,'filter':filter.op_field,'value':filter.value}
            if not fitem in request.session['filter_by']:
                request.session['filter_by'].append(fitem)
                request.session.modified = True
        if request.is_ajax():
            return index(request)
        else:
            msg = 'The filter has been loaded.'
            messages.error(request, msg) 
            return HttpResponseRedirect(reverse('reports-index'))
    except:
        error_msg = 'This filter you attempted to load does not exist'
        if request.is_ajax():    
            response = simplejson.dumps({'success':False,'data':[],'errors':error_msg,'active_filters':[],'saved_filters':[]})
            return HttpResponse(response, content_type='application/javascript; charset=utf-8')
        else:
            messages.error(request, error_msg)
            return HttpResponseRedirect(reverse('reports-index'))

@login_required
def del_filter(request, index_num):
    try:
        filter = SavedFilter.objects.get(id=int(index_num))
    except:
        error_msg = 'This filter you attempted to delete does not exist'
        if request.is_ajax():
            response = simplejson.dumps({'success':False,'data':[],'errors':error_msg,'active_filters':[],'saved_filters':[]})
            return HttpResponse(response, content_type='application/javascript; charset=utf-8')
        else:
            messages.error(request, error_msg)
            return HttpResponseRedirect(reverse('reports-index'))
    else:
        try:
            filter.delete()
        except:
            error_msg = 'Deletion of the filter failed, Try again'
            if request.is_ajax():
                response = simplejson.dumps({'success':False,'data':[],'errors':error_msg,'active_filters':[],'saved_filters':[]})
                return HttpResponse(response, content_type='application/javascript; charset=utf-8') 
            messages.error(request, error_msg)  
        if request.is_ajax():
            return index(request)
        else:
            msg = 'The filter has been deleted.'
            messages.error(request, msg) 
            return HttpResponseRedirect(reverse('reports-index'))
            
@login_required
def report(request, report_kind):
    report_kind = int(report_kind)
    template = "reports/piereport.html"
    active_filters = []
    if report_kind == 1:
        data = run_query('from_address', {'from_address__exact':""}, '-num_count', request, active_filters)
        pie_data = pack_json_data(data,'from_address','num_count')
        report_title = "Top senders by quantity"
    elif report_kind == 2:
        data = run_query('from_address', {'from_address__exact':""}, '-size', request, active_filters)
        pie_data = pack_json_data(data,'from_address','size')
        report_title = "Top senders by volume"
    elif report_kind == 3:
        data = run_query('from_domain', {'from_domain__exact':""}, '-num_count', request, active_filters)
        pie_data = pack_json_data(data,'from_domain','num_count')
        report_title = "Top sender domains by quantity"
    elif report_kind == 4:
        data = run_query('from_domain', {'from_domain__exact':""}, '-size', request, active_filters)
        pie_data = pack_json_data(data,'from_domain','size')
        report_title = "Top sender domains by volume"
    elif report_kind == 5:
        data = run_query('to_address', {'to_address__exact':""}, '-num_count', request, active_filters)
        pie_data = pack_json_data(data,'to_address','num_count')
        report_title = "Top recipients by quantity"
    elif report_kind == 6:
        data = run_query('to_address', {'to_address__exact':""}, '-size', request, active_filters)
        pie_data = pack_json_data(data,'to_address','size')
        report_title = "Top recipients by volume"
    elif report_kind == 7:
        data = run_query('to_domain', {'to_domain__exact':"", 'to_domain__isnull':False}, '-num_count', request, active_filters)
        pie_data = pack_json_data(data,'to_domain','num_count')
        report_title = "Top recipient domains by quantity"
    elif report_kind == 8:
        data = run_query('to_domain', {'to_domain__exact':"", 'to_domain__isnull':False}, '-size', request, active_filters)
        pie_data = pack_json_data(data,'to_domain','size')
        report_title = "Top recipient domains by volume"
    elif report_kind == 9:
         c = connection.cursor()
         q = "select round(sascore) as score, count(*) as count from messages"
         
         if request.session.get('filter_by', False):
             filter_list = request.session.get('filter_by')
             s = gen_dynamic_raw_query(filter_list,active_filters)
             if request.user.is_superuser:
                 c.execute(q + " WHERE " +  s[0] + " AND whitelisted=0 AND scaned > 0 GROUP BY score ORDER BY score",s[1]) 
             else:
                 sql = raw_user_filter(request)
                 c.execute(q + " WHERE " + sql + " AND "+ s[0] +" AND whitelisted=0 AND scaned > 0 GROUP BY score ORDER BY score",s[1])
         else:
             if request.user.is_superuser:
                 q = "%s WHERE whitelisted=0 AND scaned > 0 GROUP BY score ORDER BY score" % q
                 c.execute(q)
             else:
                 sql = raw_user_filter(request)
                 g = "WHERE "+sql+" AND whitelisted=0 AND scaned > 0 GROUP BY score ORDER BY score"
                 q = "%s %s" % (q,g)
                 c.execute(q)
         rows = c.fetchall()
         c.close()
         counts, scores, data = format_sa_data(rows)
         pie_data = {'scores':scores,'count':simplejson.dumps(counts)}
         template = "reports/barreport.html"
         report_title = "Spam Score distribution"
    elif report_kind == 10:
        data = run_hosts_query(request, active_filters)
        pie_data = pack_json_data(data,'clientip','num_count')
        report_title = "Top mail hosts by quantity"
        template = "reports/relays.html"
    elif report_kind == 11:
        c = connection.cursor()
        q = """SELECT date, count(*) AS mail_total,
            SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END) AS virus_total,
            SUM(CASE WHEN (virusinfected=0) AND spam>0 THEN 1 ELSE 0 END) AS spam_total,
            SUM(size) AS size_total FROM messages"""
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            s = gen_dynamic_raw_query(filter_list, active_filters)
            if request.user.is_superuser:
                c.execute(q + " WHERE " + s[0] + " GROUP BY date ORDER BY date DESC",s[1])
            else:
                sql = raw_user_filter(request)
                c.execute(q + " WHERE " + sql +" AND "+ s[0] + " GROUP BY date ORDER BY date DESC",s[1])
        else:
            if request.user.is_superuser:
                q = "%s GROUP BY date ORDER BY date DESC" % q
                c.execute(q)
            else:
                sql = raw_user_filter(request)
                q = "%s WHERE %s GROUP BY date ORDER BY date DESC" % (q,sql)
                c.execute(q)
        rows = c.fetchall()
        c.close()
        mail_total, spam_total, virus_total, dates, data = format_totals_data(rows)
        pie_data = {'dates':dates, 'mail':simplejson.dumps(mail_total), 'spam':simplejson.dumps(spam_total), 'virii':simplejson.dumps(virus_total)}
        report_title = "Total messages [ After SMTP ]"
        template = "reports/listing.html"
    
    return render_to_response(template, {'pie_data':pie_data,'top_items':data,'report_title':report_title,
        'report_kind':report_kind,'active_filters':active_filters}, context_instance=RequestContext(request))
