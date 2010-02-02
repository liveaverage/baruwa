from django.shortcuts import render_to_response
from django.db.models import Count, Sum
from baruwa.messages.models import Maillog

def index(request):
  return render_to_response('reports/index.html')

def pack_data(data,arg1,arg2):
  pie_data = {}
  n = 1
#  total = 0.0
#  for i in data:
#    total += float(i[arg2])

  for item in data:
#    v = float(item[arg2])
#    p = float(1.0 * v /total)*100
#    x = "%d%%" % p
    x = "%d" % n
#    if pie_data.has_key(x):
#      x = "%d.%d%%" % (p, n)
    pie_data[x] = item[arg2]
    n += 1
  return pie_data

def report(request,report_kind):
  import cairoplot
  colors = [(255.0/255,0.0/255,0.0/255),(222.0/255,184.0/255,135.0/255),(210.0/255,105.0/255,30.0/255),(0.0/255,139.0/255,139.0/255),(0.0/255,100.0/255,0.0/255),(255.0/255,140.0/255,0.0/255),(255.0/255,215.0/255,0.0/255),(240.0/255,230.0/255,140.0/255),(255.0/255,160.0/255,122.0/255),(0.0/255,0.0/255,0.0/255)]
  report_kind = int(report_kind)
  pie_data = {}
  data = []
  report_title = ""
  graph_name = "static/graphs/graph%d.png" % report_kind
  template = "reports/piereport.html"
  if report_kind == 1:
    data = Maillog.objects.values('from_address').filter(from_address__isnull=False).exclude(from_address = '').annotate(num_count=Count('from_address'),
      size=Sum('size')).order_by('-num_count')[:10] 
    pie_data = pack_data(data,'from_address','num_count')
    report_title = "Top senders by quantity"
  elif report_kind == 2:
    data = Maillog.objects.values('from_address').filter(from_address__isnull=False).exclude(from_address = '').annotate(num_count=Count('from_address'),
      size=Sum('size')).order_by('-size')[:10] 
    pie_data = pack_data(data,'from_address','size')
    report_title = "Top senders by volume"
  elif report_kind == 3:
    data = Maillog.objects.values('from_domain').filter(from_domain__isnull=False).exclude(from_domain = '').annotate(num_count=Count('from_domain'),
      size=Sum('size')).order_by('-num_count')[:10] 
    pie_data = pack_data(data,'from_domain','num_count')
    report_title = "Top sender domains by quantity"
  elif report_kind == 4:
    data = Maillog.objects.values('from_domain').filter(from_domain__isnull=False).exclude(from_domain = '').annotate(num_count=Count('from_domain'),
      size=Sum('size')).order_by('-size')[:10] 
    pie_data = pack_data(data,'from_domain','size')
    report_title = "Top sender domains by volume"
  elif report_kind == 5:
    data = Maillog.objects.values('to_address').filter(to_address__isnull=False).exclude(to_address = '').annotate(num_count=Count('to_address'),
      size=Sum('size')).order_by('-num_count')[:10] 
    pie_data = pack_data(data,'to_address','num_count')
    report_title = "Top recipients by quantity"
  elif report_kind == 6:
    data = Maillog.objects.values('to_address').filter(to_address__isnull=False).exclude(to_address = '').annotate(num_count=Count('to_address'),
      size=Sum('size')).order_by('-size')[:10] 
    pie_data = pack_data(data,'to_address','size')
    report_title = "Top recipients by volume"
  elif report_kind == 7:
    data = Maillog.objects.values('to_domain').filter(to_domain__isnull=False).exclude(to_domain = '').annotate(num_count=Count('to_domain'),
      size=Sum('size')).order_by('-num_count')[:10] 
    pie_data = pack_data(data,'to_domain','num_count')
    report_title = "Top recipient domains by quantity"
  elif report_kind == 8:
    data = Maillog.objects.values('to_domain').filter(to_domain__isnull=False).exclude(to_domain = '').annotate(num_count=Count('to_domain'),
      size=Sum('size')).order_by('-size')[:10] 
    pie_data = pack_data(data,'to_domain','size')
    report_title = "Top recipient domains by volume"
  elif report_kind == 12:
    data = Maillog.objects.values('clientip').filter(clientip__isnull=False).exclude(clientip = '').annotate(num_count=Count('clientip'),
      size=Sum('size'),virus_total=Sum('virusinfected'),spam_total=Sum('isspam')).order_by('-num_count')[:10]
    pie_data = pack_data(data,'clientip','num_count')
    report_title = "Top mail hosts by quantity"
    template = "reports/relays.html"
  cairoplot.pie_plot(graph_name,pie_data,450,350,None,True,True,colors)
  return render_to_response(template, {'pie_data':pie_data,'top_items':data,'graph_type':report_kind,'report_title':report_title})
