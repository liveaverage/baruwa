# 
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# vim: ai ts=4 sts=4 et sw=4
#

import email, smtplib, os, re, socket, httplib
from subprocess import Popen, PIPE
from email.Header import decode_header
from django.conf import settings
from django.core.urlresolvers import reverse
from baruwa.utils.misc import get_config_option

def return_attachment(msg, id):
    "Returns an attachment from a mime file"

    from StringIO import StringIO

    n = 1
    id = int(id)
    for message_part in msg.walk():
        content_disposition  = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions  = content_disposition.strip().split(";")
            if bool(content_disposition  and dispositions[0].lower()  == "attachment"):
                if id == n:
                    file_data  = message_part.get_payload(decode=True)
                    attachment  = StringIO(file_data)
                    attachment.content_type =  message_part.get_content_type()
                    attachment.size = len(file_data)
                    attachment.create_date =  None
                    attachment.name = None
                    attachment.mod_date =  None
                    attachment.read_date =  None
                    for param in dispositions[1:]:
                        name,value =  param.split("=")
                        name = name.lower().strip()
                        if name == "filename":
                            attachment.name = value
                        elif name == "create-date":
                            attachment.create_date =  value
                        elif name == "modification-date":
                            attachment.mod_date =  value
                        elif name == "read-date":
                            attachment.read_date =  value
                    return attachment
                    break
                n = n + 1
    return None

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
                if name.lower().strip() == "filename":
                    attachment = value
            return attachment
    return None

def get_header(header_text, default="ascii"):
    """
    Returns the headers from text
    """
    header_sections = []
    try:
        headers = decode_header(header_text)
        header_sections = [unicode(text, charset or default) for text, charset in headers]
    except:
        pass
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
        file_path = os.path.join(qdir,date,message_kind,message_id)
        if os.path.exists(file_path):
            return file_path
        file_path = os.path.join(qdir, date, message_id,'message')
        if os.path.exists(file_path):
            return file_path
    return None

def search_quarantine(date, message_id):
    """search_quarantine"""
    qdir = get_config_option('Quarantine Dir')
    date = "%s" % date
    date = date.replace('-', '')
    file_name = get_message_path(qdir, date, message_id)
    return file_name

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
            server.sendmail(from_addr, to_addr, msg)
            server.quit()
        except:
            return False
    else:
        return False
    return True

def sa_learn(mail_path, learn_as):
    """
    Spam assassin learns a message
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
            return {'success':True,'output':stdout}
        else:
            return {'success':False,'output':stderr}
    else:
        return {'success':False,'output':'mail file could not be read'}

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
    Performs a REST request and returns a JSON representation
    of the result.
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
        c.close()
    except:
        return {'success':False, 'response': 'an error occured'}

    if response.status == 200:
        return {'success':True, 'response': data}
    elif response.status == 302:
        return {'success':False, 'response': 'redirection - possible auth sync failure'}
    else:
        return {'success':False, 'response': data}

def remote_attachment_download(host, cookie, message_id, attachment_id):
    """
    Returns a email attachment from a remote node using a RESTFUL request
    """
    headers = {'Cookie':cookie,'X-Requested-With':'XMLHttpRequest'}
    resource = reverse('download-attachment', args=[message_id, attachment_id])
    rv = rest_request(host, resource, 'GET', headers)
    return rv
    
def remote_preview(host,cookie,message_id):
    """
    Returns the message preview of a message on a
    remote node using a RESTFUL request
    """
    headers = {'Cookie':cookie,'X-Requested-With':'XMLHttpRequest'}
    resource = reverse('preview-message', args=[message_id])
    rv = rest_request(host, resource, 'GET', headers)
    return rv

def remote_process(host, cookie, message_id, params):
    """
    Processes a message quarantined on a remote
    node
    """
    headers = {'Cookie':cookie,'X-Requested-With':'XMLHttpRequest'}
    resource = reverse('message-detail', args=[message_id])
    rv = rest_request(host, resource, 'POST', headers, params)
    return rv

def test_smtp_server(server, port, test_address):
    "Test smtp server delivery"
    try:
        if port == '465':
            conn = smtplib.SMTP_SSL(server)
        elif port == '25':
            conn = smtplib.SMTP(server)
        else:
            conn = smtplib.SMTP(server,port)
        conn.ehlo()
        if conn.has_extn('STARTTLS') and port != '465':
            conn.starttls()
            conn.ehlo()
        conn.docmd('MAIL FROM:', 'postmaster@baruwa.org') 
        result = conn.docmd('RCPT TO:', test_address)
        if result[0] == '250':
            return True
        else:
            return False
    except:
        return False
