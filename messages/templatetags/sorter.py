from django import template

register = template.Library()

def sorter(context, field_name, field_text):
    if context.has_key('quarantine'):
        quarantine = "quarantine"
    else:
        if context['app'] == 'messages':
            quarantine = "full"
        else:
            quarantine = None

    return { 'field_name': field_name,
        'field_text': field_text,
        'order_by': context['order_by'],
        'direction': context['direction'],
        'quarantine': quarantine,
        'app': context['app'],
    }
register.inclusion_tag('tags/sorter.html', takes_context=True)(sorter)
