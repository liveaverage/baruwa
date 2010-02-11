from django.shortcuts import render_to_response
from django.db.models import Count, Sum
from django.db import connection
from django.utils import simplejson
from messages.models import Maillog
from messages.templatetags.messages_extras import tds_get_rules

def index(request):
    return render_to_response('reports/index.html')

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
    if report_kind == 1:
        data = Maillog.objects.values('from_address').filter(from_address__isnull=False).\
        exclude(from_address = '').annotate(num_count=Count('from_address'),size=Sum('size')).order_by('-num_count')[:10] 
        pie_data = pack_data(data,'from_address','num_count')
        report_title = "Top senders by quantity"
    elif report_kind == 2:
        data = Maillog.objects.values('from_address').filter(from_address__isnull=False).\
        exclude(from_address = '').annotate(num_count=Count('from_address'),size=Sum('size')).order_by('-size')[:10] 
        pie_data = pack_data(data,'from_address','size')
        report_title = "Top senders by volume"
    elif report_kind == 3:
        data = Maillog.objects.values('from_domain').filter(from_domain__isnull=False).\
        exclude(from_domain = '').annotate(num_count=Count('from_domain'),size=Sum('size')).order_by('-num_count')[:10] 
        pie_data = pack_data(data,'from_domain','num_count')
        report_title = "Top sender domains by quantity"
    elif report_kind == 4:
        data = Maillog.objects.values('from_domain').filter(from_domain__isnull=False).\
        exclude(from_domain = '').annotate(num_count=Count('from_domain'),size=Sum('size')).order_by('-size')[:10] 
        pie_data = pack_data(data,'from_domain','size')
        report_title = "Top sender domains by volume"
    elif report_kind == 5:
        data = Maillog.objects.values('to_address').filter(to_address__isnull=False).\
        exclude(to_address = '').annotate(num_count=Count('to_address'),size=Sum('size')).order_by('-num_count')[:10] 
        pie_data = pack_data(data,'to_address','num_count')
        report_title = "Top recipients by quantity"
    elif report_kind == 6:
        data = Maillog.objects.values('to_address').filter(to_address__isnull=False).\
        exclude(to_address = '').annotate(num_count=Count('to_address'),size=Sum('size')).order_by('-size')[:10] 
        pie_data = pack_data(data,'to_address','size')
        report_title = "Top recipients by volume"
    elif report_kind == 7:
        data = Maillog.objects.values('to_domain').filter(to_domain__isnull=False).\
        exclude(to_domain = '').annotate(num_count=Count('to_domain'),size=Sum('size')).order_by('-num_count')[:10] 
        pie_data = pack_data(data,'to_domain','num_count')
        report_title = "Top recipient domains by quantity"
    elif report_kind == 8:
        data = Maillog.objects.values('to_domain').filter(to_domain__isnull=False).exclude(to_domain = '').annotate(num_count=Count('to_domain'),
            size=Sum('size')).order_by('-size')[:10] 
        pie_data = pack_data(data,'to_domain','size')
        report_title = "Top recipient domains by volume"
    elif report_kind == 9:
        scores = []
        counts = []
        data = []
        c = connection.cursor()
        c.execute("select round(sascore) as score, count(*) as count from maillog where spamwhitelisted=0 group by score order by score")
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
            size=Sum('size'),virus_total=Sum('virusinfected'),spam_total=Sum('isspam')).order_by('-num_count')[:10]
        pie_data = pack_data(data,'clientip','num_count')
        report_title = "Top mail hosts by quantity"
        template = "reports/relays.html"
    elif report_kind == 11:
        data = []
        c = connection.cursor()
        c.execute("select date, count(*) as mail_total, \
            SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END) AS virus_total, \
            SUM(CASE WHEN (virusinfected=0 OR virusinfected IS NULL) AND isspam>0 THEN 1 ELSE 0 END) as spam_total, \
            SUM(CASE WHEN (virusinfected=0 OR virusinfected IS NULL) AND (isspam=0 OR isspam IS NULL) AND ismcp>0 THEN 1 ELSE 0 END) AS mcp_total, \
            SUM(size) AS size_total FROM maillog GROUP BY date ORDER BY date DESC")
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
            #mail_total.append({'value': total, 'text':date})
            #spam_total.append({'value': spam, 'text':date})
            #virus_total.append({'value': virii, 'text':date})
            data.append({'date':date,'count':total,'virii':virii,'vpercent':vpercent,'spam':spam,'spercent':spercent,'mcp':int(rows[i][4]),'size':int(rows[i][5])})
        pie_data = {'dates':dates,'mail':simplejson.dumps(mail_total),'spam':simplejson.dumps(spam_total),'virii':simplejson.dumps(virus_total)}
        c.close()
        report_title = "Total messages [ After SMTP ]"
        template = "reports/listing.html"
    return render_to_response(template, {'pie_data':pie_data,'top_items':data,'report_title':report_title})
