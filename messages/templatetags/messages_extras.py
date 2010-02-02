# vim: ai ts=4 sts=4 et sw=4
import re,GeoIP,socket
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from baruwa.messages.models import SaRules

register = template.Library()

@register.filter(name='tds_nl_commas')
@stringfilter
def tds_nl_commas(value):
  return value.replace(',', '\n')

@register.filter(name='tds_trunc')
@stringfilter
def tds_trunc(value,arg):
  l = len(value)
  arg = int(arg)
  if l <= arg:
    return value
  else:
    suffix = '...'
    return value[0:arg] + suffix

@register.filter(name='tds_email_list')
@stringfilter
def tds_email_list(value):
  if re.match("default",value):
    value = "Any"
  return value

@register.filter(name='tds_geoip')
@stringfilter
def tds_geoip(value):
  t = ""
  m = re.match(r'(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))',value)
  if m:
    gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    try:
      cc = gip.country_code_by_addr(value).lower()
      cn = gip.country_name_by_addr(value)
    except:
      cc = None
      cn = None
    if cc and cn:
      t = '<img src="/static/imgs/flags/%s.png" alt="%s"/>' % (cc,cn)
  return mark_safe(t)

@register.filter(name='tds_hostname')
@stringfilter
def tds_hostname(value):
  hostname = ''
  m = re.match(r'(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))',value)
  if m:
    if m.groups()[0] == '127.0.0.1':
      hostname = 'localhost'
    else:
      try:
        hostname = socket.gethostbyaddr(m.groups()[0])[0]
      except:
        hostname = 'unknown'
  return mark_safe(hostname)

@register.filter(name='tds_is_learned')
@stringfilter
def tds_is_learned(value,autoescape=None):
  m = re.search(r'autolearn=((\w+\s\w+)|(\w+))',value)
  if m:
    if autoescape:
      esc = conditional_escape
    else:
      esc = lambda x: x
    r = '<span class="positive">Y</span>&nbsp;(%s)' % (esc(m.group(1)))
  else:
    r = '<span class="negative">N</span>'
  return mark_safe(r)
tds_is_learned.needs_autoescape = True

@register.inclusion_tag('tags/spamreport.html')
def spam_report(value):
  if not value:
    return ""
  return_value = []
  sa_rule_descp = ""
  m = re.search(r'\((.+?)\)',value)
  if m:
    tmp = m.groups()[0].split(',')
    for rule in tmp:
      rule = rule.lstrip()
      u = re.match(r'((\w+)(\s)(\d{1,2}\.\d{1,2}))',rule)
      if u:
        rule = u.groups()[1]
        try:
          d = SaRules.objects.get(rule__exact=rule)
        except:
          pass
        else:
          sa_rule_descp = d.rule_desc
        tdict = {'rule':rule,'score':u.groups()[3],'rule_descp':sa_rule_descp}
        return_value.append(tdict)
        sa_rule_descp = ""
  return {'rules':return_value}
