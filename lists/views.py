# vim: ai ts=4 sts=4 et sw=4

from django.shortcuts import render_to_response
from django.views.generic.list_detail import object_list
from lists.models import Blacklist, Whitelist
from lists.forms import ListAddForm,FilterForm
from django.http import HttpResponseRedirect, Http404

def index(request,list_kind=1,page=1,direction='dsc',order_by='id',search_for='',query_type=3):
    list_kind = int(list_kind)
    query_type = int(query_type)
    if query_type == 3:
        query_type = None
    ordering = order_by
    if search_for == '':
        do_filtering = False
    else:
        do_filtering = True
    
    if direction == 'dsc':
        ordering = order_by
        order_by = "-%s" % order_by

    if list_kind == 1:
        listing = Whitelist.objects.all().order_by(order_by)
    elif list_kind == 2:
        listing = Blacklist.objects.all().order_by(order_by)

    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            query_type = int(filter_form.cleaned_data['query_type'])
            search_for = filter_form.cleaned_data['search_for']
            if search_for != "" and not search_for is None:
                do_filtering = True
    if do_filtering:
        if query_type == 1:
            if ordering == 'to_address':
                listing = listing.filter(to_address__icontains=search_for)
            elif ordering == 'from_address':
                listing = listing.filter(from_address__icontains=search_for)
        else:
            if ordering == 'to_address':
                listing = listing.exclude(to_address__icontains=search_for)
            elif ordering == 'from_address':
                listing = listing.exclude(from_address__icontains=search_for)
    app = "lists/%d" % list_kind
    #return render_to_response('lists/index.html', {'list':listing,'list_kind':list_kind})
    return object_list(request,template_name='lists/index.html',queryset=listing, paginate_by=20,page=page,
        extra_context={'app':app,'list_kind':list_kind,'direction':direction,'order_by':ordering,'search_for':search_for,'query_type':query_type})

def add_to_list(request):
    template = 'lists/add.html'
    if request.method == 'GET':
        add_form = ListAddForm() 
        add_dict = {'form':add_form}
    elif request.method == 'POST':
        form = ListAddForm(request.POST) 
        if form.is_valid():
            clean_data = form.cleaned_data
            if clean_data['to_domain'] != '' and clean_data['to_address'] != 'default':
                to = "%s@%s" % (clean_data['to_address'],clean_data['to_domain'])
            elif clean_data['to_domain'] != '' and clean_data['to_address'] == 'default':
                to = clean_data['to_domain']
            else:
                to = clean_data['to_address']
            if int(clean_data['list_type']) == 1:
                wl = Whitelist(to_address=to,from_address=clean_data['from_address'])
                wl.save()
            else:
                bl = Blacklist(to_address=to,from_address=clean_data['from_address'])
                bl.save()
            return HttpResponseRedirect('/lists/')
        else:
            add_dict = {'form':form}
    return render_to_response(template,add_dict)

def delete_from_list(request, list_kind, item_id):
    item_id = int(item_id)
    list_kind = int(list_kind)
    if list_kind == 1:
        try:
            w = Whitelist.objects.get(pk=item_id)
        except Whitelist.DoesNotExist:
            raise Http404()
        else:
            w.delete()
    elif list_kind == 2:
        try:
            b = Blacklist.objects.get(pk=item_id)
        except Blacklist.DoesNotExist:
            raise Http404()
        else:
            b.delete()
    return HttpResponseRedirect('/lists/')

#fromdjango.shortcuts import get_objects_or_404
#list_item = get_object_or_404(Whitelist, pk=item_id)
#list_item.delete()
