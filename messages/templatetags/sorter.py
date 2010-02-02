from django import template

register = template.Library()

def sorter(context, field_name, field_text):
  if context['quarantine']:
    quarantine = "quarantine"
  else:
    quarantine = "full"

  return { 'field_name': field_name,
      'field_text': field_text,
      'order_by': context['order_by'],
      'direction': context['direction'],
      'quarantine': quarantine,
      }
register.inclusion_tag('tags/sorter.html', takes_context=True)(sorter)
