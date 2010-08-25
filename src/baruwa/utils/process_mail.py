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

import smtplib, os, re, socket, httplib
from subprocess import Popen, PIPE
from django.conf import settings
from django.core.urlresolvers import reverse
from baruwa.utils.misc import get_config_option


def get_message_path(qdir, date, message_id):
    """
    Returns the on disk path of a message
    or None if path does not exist
    """
    qdirs = ["spam", "nonspam", "mcp"]
    for message_kind in qdirs:
        file_path = os.path.join(qdir, date, message_kind, message_id)
        if os.path.exists(file_path):
            return file_path
        file_path = os.path.join(qdir, date, message_id, 'message')
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
        mail_file = open(mail_path, 'r')
        msg = mail_file.read()
        mail_file.close()
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
    sa_learn_cmd = ['/usr/bin/sa-learn', learn, mail_path]
    learn_opts = ('spam', 'ham', 'forget')

    if not learn_as in learn_opts:
        return {'success': False, 'output': '',
         'errormsg': 'Incorrect learn option'}
    if os.path.exists(mail_path):
        pipe = Popen(sa_learn_cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = pipe.communicate()
        if pipe.returncode == 0:
            return {'success': True, 'output': stdout}
        else:
            return {'success': False, 'output': stderr}
    else:
        return {'success': False, 'output': 'mail file could not be read'}

def clean_regex(rule):
    """
    Formats a regex for parsing MailScanner
    configs
    """
    if rule == 'default' or rule == '*':
        rule = '*@*'
    if not '@' in rule:
        if re.match(r'^\*', rule):
            rule = "*@%s" % rule
        else:
            rule = "*@%s" % rule
    if re.match(r'^@', rule):
        rule = "*%s" % rule
    if re.match(r'@$', rule):
        rule = "%s*" % rule
    rule = re.sub(r'\*', '.*', rule)
    rule = "^%s\.?$" % rule
    return rule

def host_is_local(host):
    """
    Checks if host is local to host running the function
    """
    host_name = socket.gethostbyname(host)
    ip_addr = socket.gethostbyname(socket.gethostname())
    if host_name in [ip_addr, '127.0.0.1']:
        return True
    else:
        return False

def rest_request(host, resource, method, headers, params=None):
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
        conn = httplib.HTTPConnection(host)
        conn.request(method, resource, params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except:
        return {'success': False, 'response': 'an error occured'}

    if response.status == 200:
        return {'success': True, 'response': data}
    elif response.status == 302:
        return {'success': False, 
        'response': 'redirection - possible auth sync failure'}
    else:
        return {'success': False, 'response': data}

#TODO
# Use a Class for DRY
def remote_attachment_download(host, cookie, message_id, 
                                attachment_id, archived):
    """
    Returns a email attachment from a remote node using a RESTFUL request
    """
    headers = {'Cookie': cookie, 'X-Requested-With': 'XMLHttpRequest'}
    if archived:
        resource = reverse('archive-download-attachment', 
                        args=[message_id, attachment_id])
    else:
        resource = reverse('download-attachment', 
                        args=[message_id, attachment_id])
    return rest_request(host, resource, 'GET', headers)

def remote_preview(host, cookie, message_id, archived):
    """
    Returns the message preview of a message on a
    remote node using a RESTFUL request
    """
    headers = {'Cookie':cookie, 'X-Requested-With':'XMLHttpRequest'}
    if archived:
        resource = reverse('archive-preview-message', args=[message_id])
    else:
        resource = reverse('preview-message', args=[message_id])
    return rest_request(host, resource, 'GET', headers)

def remote_process(host, cookie, message_id, params):
    """
    Processes a message quarantined on a remote
    node
    """
    headers = {'Cookie':cookie, 'X-Requested-With':'XMLHttpRequest'}
    resource = reverse('message-detail', args=[message_id])
    return rest_request(host, resource, 'POST', headers, params)

def remote_release(host, message_uuid):
    "Release a message quarantined on a remote host"
    headers = {'X-Requested-With':'XMLHttpRequest'}
    resource = reverse('auto-release', args=[message_uuid])
    return rest_request(host, resource, 'GET', headers)


def test_smtp_server(server, port, test_address):
    "Test smtp server delivery"
    try:
        port = int(port)
        if port == 465:
            conn = smtplib.SMTP_SSL(server)
        elif port == 25:
            conn = smtplib.SMTP(server)
        else:
            conn = smtplib.SMTP(server, port)
        #conn.set_debuglevel(5)
        conn.ehlo()
        if conn.has_extn('STARTTLS') and port != 465:
            conn.starttls()
            conn.ehlo()
        conn.docmd('MAIL FROM:', 'postmaster@baruwa.org')
        result = conn.docmd('RCPT TO:', test_address)
        if conn:
            conn.quit()
        if result[0] == 250:
            return True
        else:
            return False
    except:
        return False
