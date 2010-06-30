from django import template

register = template.Library()

def pagination_heading(context):
    if context.has_key('page'):
        return {'page': context['page'], 'pages': context['pages']}
    else:
        return {'page': 1, 'pages': 1}
register.inclusion_tag('tags/pagination_heading.html', takes_context=True)(pagination_heading)
