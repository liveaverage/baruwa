# vim: ai ts=4 sts=4 et sw=4

from django.shortcuts import render_to_response
from baruwa.lists.models import Blacklist, Whitelist
from baruwa.lists.forms import ListAddForm
from django.http import HttpResponseRedirect, Http404

def index(request):
  blacklist = Blacklist.objects.all()
  whitelist = Whitelist.objects.all()

  return render_to_response('lists/index.html', {'whitelist':whitelist, 'blacklist':blacklist})

def add_to_list(request):
  template = 'lists/add.html'
  if request.method == 'GET':
    add_form = ListAddForm() 
    add_dict = {'form':add_form}
  elif request.method == 'POST':
    form = ListAddForm(request.POST) 
    if form.is_valid():
      clean_data = form.cleaned_data
      if int(clean_data['list_type']) == 1:
        wl = Whitelist(to_address=clean_data['to_address'],from_address=clean_data['from_address'])
        wl.save()
      else:
        bl = Blacklist(to_address=clean_data['to_address'],from_address=clean_data['from_address'])
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
