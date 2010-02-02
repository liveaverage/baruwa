from django import template

register = template.Library()

def pagination_heading(context):
    return {
        'page': context['page'],
        'pages': context['pages'],
    }
register.inclusion_tag('tags/pagination_heading.html', takes_context=True)(pagination_heading)
