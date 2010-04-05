#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# vim: ai ts=4 sts=4 et sw=4
import email,smtplib,os,re,socket,httplib
from subprocess import Popen, PIPE
from email.Header import decode_header
from django.conf import settings

def parse_attachment(part):
    """
    Parses an email part and returns attachment name
    """
    attachment = ""
    content_disposition = part.get("Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and dispositions[0].lower() == "attachment"):
            for param in dispositions[1:]:
                name,value = param.split("=")
                if name.lstrip() == "filename":
                    attachment = value
            return attachment
    return None

def get_header(header_text, default="ascii"):
    """
    Returns the headers from text
    """
    headers = decode_header(header_text)
    header_sections = [unicode(text, charset or default) for text, charset in headers]
    return u"".join(header_sections)

def parse_email(msg):
    """
    Parses an email and returns a dict representing 
    the message
    """
    attachments = []
    body = None
    html = None
    has_html = False

    for part in msg.walk():
        attach = parse_attachment(part)
        if attach:
            attachments.append(attach)
        elif part.get_content_type() == "text/plain":
            if body is None:
                body = ""
            try:
                body += unicode(part.get_payload(decode=True),part.get_content_charset(),'replace').encode('utf8','replace')
            except:
                pass
        elif part.get_content_type() == "text/html":
            has_html = True
            if html is None:
                html = ""
            try:
                html += unicode(part.get_payload(decode=True),part.get_content_charset(),'replace').encode('utf8','replace')
            except:
                pass
    return {
        'subject' : get_header(msg.get('Subject')),
        'to' : get_header(msg.get('To')),
        'from' : get_header(msg.get('From')),
        'date' : get_header(msg.get('Date')),
        'has_html' : has_html,
        'body' : body,
        'html' : html,
        'attachments' : attachments,
    }

def get_message_path(qdir,date,message_id):
    """
    Returns the on disk path of a message
    or None if path does not exist
    """
    qdirs = ["spam","nonspam","mcp"]
    for message_kind in qdirs:
        file_path = "%s/%s/%s/%s" % (qdir,date,message_kind,message_id)
        if os.path.exists(file_path):
            return file_path
        file_path = "%s/%s/%s/message" % (qdir, date, message_id)
        if os.path.exists(file_path):
            return file_path
        else:
            return None

def release_mail(mail_path, to_addr, from_addr):
    """
    Releases a message from the quarantine
    """
    msg = ""
    host = settings.EMAIL_HOST
    if os.path.exists(mail_path):
        file = open(mail_path)
        for line in file:
            msg = msg + line
        try:
            server = smtplib.SMTP(host)
        except:
            return False
        try:
            server.sendmail(from_addr, to_addr, msg)
        except:
            server.quit()
            return False
        server.quit()
    else:
        return False
    return True

def sa_learn(mail_path, learn_as):
    """
    Spam assassin learn a message
    """
    learn = "--%s" % learn_as
    SA_LEARN = ['/usr/bin/sa-learn',learn,mail_path]
    LEARN_OPTS = ('spam','ham','forget')

    if not learn_as in LEARN_OPTS:
        return {'success':False,'output':'','errormsg':'Incorrect learn option'}
    if os.path.exists(mail_path):
        p = Popen(SA_LEARN, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            return {'success':True,'output':stdout,'errormsg':''}
        else:
            return {'success':False,'output':stdout,'errormsg':stderr}
    else:
        return {'success':False,'output':'','errormsg':'mail file could not be read'}

def get_config_option(search_option):
    """
    Return a MailScanner config setting from the
    config file
    """
    #config = settings.MS_CONFIG
    config = getattr(settings, 'MS_CONFIG', '/etc/MailScanner/MailScanner.conf')
    COMMENT_CHAR = '#'
    OPTION_CHAR =  '='
    value = ''
    if os.path.exists(config):
        f = open(config)
        for line in f:
            if COMMENT_CHAR in line:
                line, comment = line.split(COMMENT_CHAR, 1)
            if OPTION_CHAR in line:
                option, value = line.split(OPTION_CHAR, 1)
                option = option.strip()
                value = value.strip()
                if search_option == option:
                    break
        f.close()
    return value

def clean_regex(rule):
    """
    Formats a regex for parsing MailScanner
    configs
    """
    if rule == 'default' or rule == '*':
        rule = '*@*'
    if not '@' in rule:
        if re.match(r'^\*',rule):
            rule = "*@%s" % rule
        else:
            rule = "*@%s" % rule
    if re.match(r'^@',rule):
        rule = "*%s" % rule
    if re.match(r'@$',rule):
        rule = "%s*" % rule
    rule = re.sub(r'\*','.*',rule)
    rule = "^%s\.?$" % rule
    return rule

def host_is_local(host):
    """
    Checks if host is local to host running the function
    """
    h = socket.gethostbyname(host)
    ip = socket.gethostbyname(socket.gethostname())
    if h in [ip,'127.0.0.1']:
        return True
    else:
        return False

def rest_request(host,resource,method,headers,params=None):
    """
    Performs a REST request
    """
    data = ''

    if not resource.startswith('/'):
        resource = '/' + resource
    if not resource.endswith('/'):
        resource = resource + '/'

    try:
        c = httplib.HTTPConnection(host)
        r = c.request(method,resource,params,headers)
        response = c.getresponse()
        data = response.read()
    except:
        return {'success':False,'response':'an error occured'}
    else:
        c.close()
    if response.status == 200:
        return {'success':True,'response':data}
    else:
        return {'success':False,'response':data}
