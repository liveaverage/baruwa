from django.shortcuts import render_to_response
from django.db.models import Count, Sum, Max, Min, Q
from django.db import connection
from django.utils import simplejson
from messages.models import Maillog
from reports.forms import FilterForm,FILTER_ITEMS,FILTER_BY
from messages.templatetags.messages_extras import tds_get_rules
from django.forms.util import ErrorList as errorlist
from django.http import HttpResponseRedirect
#import random
#from collections import defaultdict


def to_dict(tuple_list):
    d = {}
    for i in tuple_list:
      d[i[0]] = i[1] 
    return d

def r_query(filter_list,active_filters=None):
    filter_items = to_dict(list(FILTER_ITEMS))
    filter_by = to_dict(list(FILTER_BY))
    sql = []
    vals = []
    for filter_item in filter_list:
        if filter_item['filter'] == '1':
            tmp = "%s = %%s" % filter_item['field']
            sql.append(tmp)
            vals.append(filter_item['value'])
        if filter_item['filter'] == '2':
            tmp = "%s != %%s" % filter_item['field']
            sql.append(tmp)
            vals.append(filter_item['value'])
        if filter_item['filter'] == '3':
            tmp = "%s > %%d" % filter_item['field']
            sql.append(tmp)
            vals.append(filter_item['value'])
        if filter_item['filter'] == '4':
            tmp = "%s < %%d" % filter_item['field']
            sql.append(tmp)
            vals.append(filter_item['value'])
        if filter_item['filter'] == '5':
            tmp = "%s LIKE %%s" % filter_item['field']
            sql.append(tmp)
            vals.append('%'+filter_item['value']+'%')
        if filter_item['filter'] == '6':
            tmp = "%s NOT LIKE %%s" % filter_item['field']
            sql.append(tmp)
            vals.append('%'+filter_item['value']+'%')
        if filter_item['filter'] == '7':
            tmp = "%s REGEXP %%s" % filter_item['field']
            sql.append(tmp)
            vals.append(filter_item['value'])
        if filter_item['filter'] == '8':
            tmp = "%s NOT REGEXP %%s" % filter_item['field']
            sql.append(tmp)
            vals.append(filter_item['value'])
        if filter_item['filter'] == '9':
            tmp = "%s IS NULL" % filter_item['field']
            sql.append(tmp)
        if filter_item['filter'] == '10':
            tmp = "%s IS NOT NULL" % filter_item['field']
            sql.append(tmp)
        if filter_item['filter'] == '11':
            tmp = "%s > 0" % filter_item['field']
            sql.append(tmp)
        if filter_item['filter'] == '12':
            tmp = "%s = 0" % filter_item['field']
            sql.append(tmp)
        if not active_filters is None:
            active_filters.append({'filter_field':filter_items[filter_item['field']],'filter_by':filter_by[int(filter_item['filter'])],'filter_value':filter_item['value']})
    return (' AND '.join(sql),vals)

def d_query(model,filter_list,active_filters=None):
    kwargs = {}
    nkwargs = {}
    nargs = []
    largs = []
    filter_items = to_dict(list(FILTER_ITEMS))
    filter_by = to_dict(list(FILTER_BY))
    for filter_item in filter_list:
        if filter_item['filter'] == '1':
            tmp = "%s__exact" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
                kwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '2':
            tmp = "%s__exact" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                del nkwargs[tmp]
            else:
			    nkwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '3':
            tmp = "%s__qt" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
                kwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '4':
            tmp = "%s__lt" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
                kwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '5':
            tmp = "%s__icontains" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
			    kwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '6':
            tmp = "%s__icontains" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                del nkwargs[tmp]
            else:
			    nkwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '7':
            tmp = "%s__regex" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
			    kwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '8':
            tmp = "%s__regex" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str(filter_item['value'])}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                del nkwargs[tmp]
            else:
			    nkwargs.update({str(tmp):str(filter_item['value'])})
        if filter_item['filter'] == '9':
            tmp = "%s__isnull" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str('True')}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
			    kwargs.update({str(tmp):str('True')})
        if filter_item['filter'] == '10':
            tmp = "%s__isnull" % filter_item['field']
            if nkwargs.has_key(tmp):
                kw = {str(tmp):str('True')}
                nargs.append(Q(**kw))
                kw = {str(tmp):str(nkwargs[tmp])}
                nargs.append(Q(**kw))
                del nkwargs[tmp]
            else:
			    nkwargs.update({str(tmp):str('True')})
        if filter_item['filter'] == '11':
            tmp = "%s__gt" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str('0')}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
			    kwargs.update({str(tmp):str('0')})
        if filter_item['filter'] == '12':
            tmp = "%s__exact" % filter_item['field']
            if kwargs.has_key(tmp):
                kw = {str(tmp):str('0')}
                largs.append(Q(**kw))
                kw = {str(tmp):str(kwargs[tmp])}
                largs.append(Q(**kw))
                del kwargs[tmp]
            else:
			    kwargs.update({str(tmp):str('0')})
        if not active_filters is None:
			active_filters.append({'filter_field':filter_items[filter_item['field']],'filter_by':filter_by[int(filter_item['filter'])],'filter_value':filter_item['value']})
    if kwargs:
        model = model.filter(**kwargs)
    if nkwargs:
        model = model.exclude(**nkwargs)
    if nargs:
        q = Q()
        for query in nargs:
            q = q | query
        model = model.exclude(q)
    if largs:
        q = Q()
        for query in largs:
            q = q | query
        model = model.filter(q)
    return model

def apply_filter(model,request,active_filters):
    if request.session.get('filter_by', False):
        filter_list = request.session.get('filter_by')
        model = d_query(model,filter_list,active_filters)
    return model

def index(request):
    errors = None
    data = Maillog.objects
    active_filters = [] 
    if request.method == 'POST':
        if request.session.test_cookie_worked() or request.session.get('filter_by', False):
            try:
                request.session.delete_test_cookie()
            except:
                pass
            filter_form = FilterForm(request.POST)
            if filter_form.is_valid():
                cleaned_data = filter_form.cleaned_data
                if not request.session.get('filter_by', False):
                    request.session['filter_by'] = []
                    #id = random.randrange(4000,10000)
                    #request.session['filter_ids'] = [id]
                    request.session['filter_by'].append({'field':cleaned_data['filtered_field'],
                        'filter':cleaned_data['filtered_by'],'value':cleaned_data['filtered_value']})
                else:
                    #id = random.randrange(4000,10000)
                    #while (id in request.session['filter_ids']):
                    #    id = random.randrange(4000,10000)
                    fitem = {'field':cleaned_data['filtered_field'],'filter':cleaned_data['filtered_by'],
                        'value':cleaned_data['filtered_value']}
                    #request.session['filter_ids'].append(id)
                    if not fitem in request.session['filter_by']:
                        request.session['filter_by'].append(fitem)
                        request.session.modified = True
                filter_list = request.session.get('filter_by')
                data = d_query(data,filter_list,active_filters)
            else:
                error_list = filter_form.errors.values()[0]
                errors = errorlist(error_list).as_ul()
                if request.session.get('filter_by', False):
                    filter_list = request.session.get('filter_by')
                    data = d_query(data,filter_list,active_filters)
        else:
            filter_form = FilterForm()
            errors = 'Cookies are not enabled, please enable cookies'
    else:
        filter_form = FilterForm()
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            data = d_query(data,filter_list,active_filters)
        else:
            request.session.set_test_cookie()
    data = data.aggregate(count=Count('timestamp'),newest=Max('timestamp'),oldest=Min('timestamp'))
    return render_to_response('reports/index.html',
        #{'form':filter_form,'data':data,'errors':errors,'active_filters':request.session['filter_by']})
        {'form':filter_form,'data':data,'errors':errors,'active_filters':active_filters})

def del_filter(request,index):
    if request.session.get('filter_by', False):
        li = request.session.get('filter_by')
        li.remove(li[int(index)])
        request.session.modified = True
    return HttpResponseRedirect('/reports/')

def pack_data(data,arg1,arg2):
    rv = []
    colors = ['red','#ffa07a','#deb887','#d2691e','#008b8b','#006400','#ff8c00','#ffd700','#f0e68c','#000000']
    n = 0
    for item in data:
        pie_data = {}
        pie_data['y'] = item[arg2]
        #pie_data['text'] = item[arg1]
        pie_data['color'] = colors[n]
        pie_data['stroke'] = 'black'
        pie_data['tooltip'] = item[arg1]
        rv.append(pie_data)
        n += 1
    return simplejson.dumps(rv)

def report(request,report_kind):
    report_kind = int(report_kind)
    template = "reports/piereport.html"
    active_filters = []
    if report_kind == 1:
        data = Maillog.objects.values('from_address').\
        exclude(from_address = '').annotate(num_count=Count('from_address'),size=Sum('size')).order_by('-num_count')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'from_address','num_count')
        report_title = "Top senders by quantity"
    elif report_kind == 2:
        data = Maillog.objects.values('from_address').\
        exclude(from_address = '').annotate(num_count=Count('from_address'),size=Sum('size')).order_by('-size')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'from_address','size')
        report_title = "Top senders by volume"
    elif report_kind == 3:
        data = Maillog.objects.values('from_domain').filter(from_domain__isnull=False).\
        exclude(from_domain = '').annotate(num_count=Count('from_domain'),size=Sum('size')).order_by('-num_count')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'from_domain','num_count')
        report_title = "Top sender domains by quantity"
    elif report_kind == 4:
        data = Maillog.objects.values('from_domain').filter(from_domain__isnull=False).\
        exclude(from_domain = '').annotate(num_count=Count('from_domain'),size=Sum('size')).order_by('-size')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'from_domain','size')
        report_title = "Top sender domains by volume"
    elif report_kind == 5:
        data = Maillog.objects.values('to_address').\
        exclude(to_address = '').annotate(num_count=Count('to_address'),size=Sum('size')).order_by('-num_count')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'to_address','num_count')
        report_title = "Top recipients by quantity"
    elif report_kind == 6:
        data = Maillog.objects.values('to_address').\
        exclude(to_address = '').annotate(num_count=Count('to_address'),size=Sum('size')).order_by('-size')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'to_address','size')
        report_title = "Top recipients by volume"
    elif report_kind == 7:
        data = Maillog.objects.values('to_domain').filter(to_domain__isnull=False).\
        exclude(to_domain = '').annotate(num_count=Count('to_domain'),size=Sum('size')).order_by('-num_count')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'to_domain','num_count')
        report_title = "Top recipient domains by quantity"
    elif report_kind == 8:
        data = Maillog.objects.values('to_domain').filter(to_domain__isnull=False).exclude(to_domain = '').annotate(num_count=Count('to_domain'),
            size=Sum('size')).order_by('-size') 
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'to_domain','size')
        report_title = "Top recipient domains by volume"
    elif report_kind == 9:
        scores = []
        counts = []
        data = []
        c = connection.cursor()
        q = "select round(sascore) as score, count(*) as count from maillog"
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            s = r_query(filter_list,active_filters)
            c.execute(q + " WHERE " +  s[0] + " AND spamwhitelisted=0 GROUP BY score ORDER BY score",s[1]) 
        else:
            q = "%s WHERE spamwhitelisted=0 GROUP BY score ORDER BY score" % q
            c.execute(q)
        rows = c.fetchall()
        for i in range(len(rows)):
            score = "%s" % rows[i][0]
            count = int(rows[i][1])
            counts.append(count)
            scores.append(score)
            data.append({'score':score,'count':count})
        c.close()
        pie_data = {'scores':scores,'count':simplejson.dumps(counts)}
        template = "reports/barreport.html"
        report_title = "Spam Score distribution"
    elif report_kind == 10:
        data = Maillog.objects.values('clientip').filter(clientip__isnull=False).exclude(clientip = '').annotate(num_count=Count('clientip'),
            size=Sum('size'),virus_total=Sum('virusinfected'),spam_total=Sum('isspam')).order_by('-num_count')
        data = apply_filter(data,request,active_filters)
        data = data[:10]
        pie_data = pack_data(data,'clientip','num_count')
        report_title = "Top mail hosts by quantity"
        template = "reports/relays.html"
    elif report_kind == 11:
        data = []
        c = connection.cursor()
        q = """select date, count(*) as mail_total,
            SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END) AS virus_total,
            SUM(CASE WHEN (virusinfected=0 OR virusinfected IS NULL) AND isspam>0 THEN 1 ELSE 0 END) as spam_total,
            SUM(CASE WHEN (virusinfected=0 OR virusinfected IS NULL) AND (isspam=0 OR isspam IS NULL) AND ismcp>0 THEN 1 ELSE 0 END) AS mcp_total,
            SUM(size) AS size_total FROM maillog"""
        if request.session.get('filter_by', False):
            filter_list = request.session.get('filter_by')
            s = r_query(filter_list,active_filters)
            c.execute(q + " WHERE " + s[0] + " GROUP BY date ORDER BY date DESC",s[1])
        else:
            q = "%s GROUP BY date ORDER BY date DESC" % q
            c.execute(q)
        rows = c.fetchall()
        mail_total = []
        spam_total = []
        virus_total = []
        dates = []
        for i in range(len(rows)):
            date = "%s" % rows[i][0]
            total = int(rows[i][1])
            virii = int(rows[i][2])
            spam = int(rows[i][3])
            vpercent = "%.1f" % ((1.0 * virii/total)*100)
            spercent = "%.1f" % ((1.0 * spam/total)*100)
            mail_total.append(total)
            spam_total.append(spam)
            virus_total.append(virii)
            dates.append(date)
            data.append({'date':date,'count':total,'virii':virii,'vpercent':vpercent,'spam':spam,'spercent':spercent,'mcp':int(rows[i][4]),'size':int(rows[i][5])})
        pie_data = {'dates':dates,'mail':simplejson.dumps(mail_total),'spam':simplejson.dumps(spam_total),'virii':simplejson.dumps(virus_total)}
        c.close()
        report_title = "Total messages [ After SMTP ]"
        template = "reports/listing.html"
    return render_to_response(template, {'pie_data':pie_data,'top_items':data,'report_title':report_title,'active_filters':active_filters})
