#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2011  Andrew Colin Kissa <andrew@topdog.za.net>
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

"Baruwa email message related modules"
import os
import email
import base64
import codecs
import shutil
import socket
import smtplib

from StringIO import StringIO
from email.Header import decode_header
from subprocess import Popen, PIPE

from lxml.html.clean import Cleaner
from lxml.html import tostring, fromstring, iterlinks

from django.utils.translation import ugettext as _
from django.conf import settings

from baruwa.utils.misc import get_config_option
from baruwa.utils.regex import MSGID_RE, HTMLTITLE_RE

NOTFOUND = object()
UNCLEANTAGS = ['html', 'head', 'link', 'a', 'body', 'base']


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
        if settings.DEBUG:
            conn.set_debuglevel(5)
        conn.ehlo()
        if conn.has_extn('STARTTLS') and port != 465:
            conn.starttls()
            conn.ehlo()
        conn.docmd('MAIL FROM:', 'postmaster@baruwa.org')
        result = conn.docmd('RCPT TO:', test_address)
        if conn:
            conn.quit()
        if result[0] in range(200, 299):
            return True
        else:
            return False
    except (smtplib.SMTPException, socket.error):
        return False


def get_message_path(qdir, date, message_id):
    """
    Returns the on disk path of a message
    or None if path does not exist
    """
    file_path = os.path.join(qdir, date, message_id, 'message')
    if os.path.exists(file_path):
        return file_path, True

    qdirs = ["spam", "nonspam", "mcp"]
    for message_kind in qdirs:
        file_path = os.path.join(qdir, date, message_kind, message_id)
        if os.path.exists(file_path):
            return file_path, False
    return None, None


def search_quarantine(date, message_id):
    """search_quarantine"""
    qdir = get_config_option('Quarantine Dir')
    date = "%s" % date
    date = date.replace('-', '')
    file_name = get_message_path(qdir, date, message_id)
    return file_name


class EmailParser(object):
    """Parses a email message"""

    def process_headers(self, msg):
        "Populate the headers"
        headers = {}
        headers['subject'] = self.get_header(msg['Subject'])
        headers['to'] = self.get_header(msg['To'])
        headers['from'] = self.get_header(msg['From'])
        headers['date'] = self.get_header(msg['Date'])
        headers['message-id'] = self.get_header(msg['Message-ID'])
        return headers

    def get_header(self, header_text, default="ascii"):
        "Decode and return the header"
        if not header_text:
            return header_text

        sections = decode_header(header_text)
        return ' '.join(section.decode(enc or default, 'replace')
        for section, enc in sections)

    def parse_msg(self, msg):
        "Parse a message and return a dict"
        parts = []
        attachments = []

        headers = self.process_headers(msg)
        self.process_msg(msg, parts, attachments)
        return dict(headers=headers, parts=parts, attachments=attachments,
                    content_type='message/rfc822')

    def parse_attached_msg(self, msg):
        "Parse and attached message"
        content_type = msg.get_content_type()
        return dict(filename='rfc822.txt', content_type=content_type)

    def process_msg(self, message, parts, attachments):
        "Recursive message processing"

        content_type = message.get_content_type()
        attachment = message.get_param('attachment',
                    NOTFOUND, 'Content-Disposition')
        if content_type == 'message/rfc822':
            [attachments.append(self.parse_attached_msg(msg))
                for msg in message.get_payload()]
            return True

        if message.is_multipart():
            if content_type == 'multipart/alternative':
                for par in reversed(message.get_payload()):
                    if self.process_msg(par, parts, attachments):
                        return True
            else:
                [self.process_msg(par, parts, attachments)
                    for par in message.get_payload()]
            return True
        success = False

        if (content_type == 'text/html'
            and attachment is NOTFOUND):
            parts.append({'type': 'html',
                'content': self.return_html_part(message)})
            success = True
        elif (content_type.startswith('text/')
                and attachment is NOTFOUND):
            parts.append({'type': 'text',
                'content': self.return_text_part(message)})
            success = True
        filename = message.get_filename(None)
        if filename and not attachment is NOTFOUND:
            attachments.append(
                dict(filename=self.get_header(filename),
                content_type=content_type))
            success = True
        return success

    def return_text_part(self, part):
        "Encodes the message as utf8"
        body = part.get_payload(decode=True)
        charset = part.get_content_charset('latin1')
        try:
            codecs.lookup(charset)
        except LookupError:
            charset = 'ascii'
        return body.decode(charset, 'replace')

    def return_html_part(self, part):
        "Sanitize the html and return utf8"
        body = part.get_payload(decode=True)
        charset = part.get_content_charset('latin1')
        try:
            codecs.lookup(charset)
        except LookupError:
            charset = 'ascii'
        #return self.sanitize_html(body.decode(charset, 'replace'))
        return self.sanitize_html(body)

    def get_attachment(self, msg, attach_id):
        "Get and return an attachment"
        num = 0
        attach_id = int(attach_id)

        for part in msg.walk():
            attachment = part.get_param('attachment',
                        NOTFOUND, 'Content-Disposition')
            if not attachment is NOTFOUND:
                filename = part.get_filename(None)
                if filename:
                    filename = filename.replace(' ', '_')
                    num += 1
                if attach_id == num:
                    if part.is_multipart():
                        data = part.as_string()
                    else:
                        data = part.get_payload(decode=True)
                    attachment = StringIO(data)
                    attachment.content_type = part.get_content_type()
                    attachment.size = len(data)
                    attachment.name = filename
                    return attachment
        return None

    def sanitize_html(self, msg):
        "Clean up html"
        cleaner = Cleaner(style=True, remove_tags=UNCLEANTAGS)
        msg = HTMLTITLE_RE.sub('', msg)
        html = cleaner.clean_html(msg)
        html = fromstring(html)
        for element, attribute, link, pos in iterlinks(html):
            element.attrib['src'] = settings.MEDIA_URL + '/imgs/blocked.gif'
        return tostring(html)


class ProcessQuarantinedMessage(object):
    """Process a quarantined message"""
    def __init__(self, messageid, date, host=None):
        "init"
        self.messageid = messageid
        self.date = date
        path, isdir = search_quarantine(date, messageid)
        assert path, _("Message not found in the quarantine")
        self.path = path
        self.isdir = isdir
        self.host = settings.EMAIL_HOST
        self.errors = []
        self.output = ''
        if host:
            self.host = host

    def release(self, from_addr, to_addrs):
        "Release message from quarantine"
        try:
            messagefile = open(self.path, 'r')
            message = messagefile.readlines()
            messagefile.close()
            for index, line in enumerate(message):
                if line.endswith(' ret-id none;\n'):
                    message[index] = line.replace(' ret-id none;', '')
                if MSGID_RE.match(line):
                    message.pop(index)
                    break
            message = ''.join(message)

            smtp = smtplib.SMTP(self.host)
            if settings.DEBUG:
                smtp.set_debuglevel(5)
            smtp.sendmail(from_addr, to_addrs, message)
            smtp.quit()
        except IOError:
            self.errors.append(_('The quarantined message not found'))
            return False
        except smtplib.SMTPException, exception:
            self.errors.append(str(exception))
            return False
        return True

    def learn(self, learnas):
        "Bayesian learn the message"
        learnopts = ('spam', 'ham', 'forget')
        if not learnas in learnopts:
            self.errors.append(_('Unsupported learn option supplied'))
            return False
        if not os.path.exists(self.path):
            self.errors.append(_('The quarantined message not found'))
            return False

        try:
            learn = "--%s" % learnas
            sa_learn_cmd = ['sa-learn', learn, self.path]
            pipe = Popen(sa_learn_cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = pipe.communicate()
            if pipe.returncode == 0:
                self.output = stdout
                return True
            else:
                self.errors.append(stderr)
                self.output = stderr
                return False
        except OSError, exception:
            self.errors.append(str(exception))
            return False

    def delete(self):
        "Delete quarantined file"
        try:
            if '..' in self.path:
                raise OSError('Attempted directory traversal')
            if self.isdir:
                path = os.path.dirname(self.path)
                shutil.rmtree(path)
            else:
                os.remove(self.path)
        except OSError, exception:
            self.errors.append(str(exception))
            return False
        return True

    def reset_errors(self):
        "Resets errors"
        self.errors[:] = []


class PreviewMessage(object):
    """Preview message"""
    def __init__(self, messageid, date):
        "init"
        self.messageid = messageid
        self.date = date
        path, isdir = search_quarantine(date, messageid)
        assert path, _("Message not found in the quarantine")
        self.path = path
        self.isdir = isdir
        self.parser = EmailParser()
        fip = open(self.path, 'r')
        self.msg = email.message_from_file(fip)
        fip.close()

    def preview(self):
        "Return message"
        return self.parser.parse_msg(self.msg)

    def attachment(self, attachmentid):
        "Return attachment"
        attachment = self.parser.get_attachment(self.msg, attachmentid)
        if attachment:
            msgdict = {}
            msgdict['mimetype'] = attachment.content_type
            msgdict['attachment'] = base64.encodestring(attachment.getvalue())
            msgdict['name'] = attachment.name
            attachment.close()
            return msgdict
        return None


class TestDeliveryServers(object):
    """Test deliverying mail to a server"""
    def __init__(self, host, port, test_addr, from_addr):
        "init"
        self.host = host
        self.port = int(port)
        self.has_ssl = False
        self.has_starttls = False
        self.debug = False
        self.errors = []
        self.test_addr = test_addr
        self.from_addr = from_addr

    def smtp_test(self):
        "run smtp test"
        try:
            if self.port == 465:
                self.conn = smtplib.SMTP_SSL(self.host)
                self.has_ssl = True
            elif self.port == 25:
                self.conn = smtplib.SMTP(self.host)
            else:
                self.conn = smtplib.SMTP(self.host, self.port)
            if self.debug:
                self.conn.set_debuglevel(5)
            self.conn.ehlo()
            if self.conn.has_extn('STARTTLS') and self.port != 465:
                self.conn.starttls()
                self.conn.ehlo()
                self.has_starttls = True
            self.conn.docmd('MAIL FROM:', self.from_addr)
            result = self.conn.docmd('RCPT TO:', self.test_addr)
            if self.conn:
                self.conn.quit()
            if result[0] in range(200, 299):
                return True
            else:
                self.errors.append(
                _('Expected response code 2xx got %(code)s') % {
                'code': str(result[0])})
                return False
        except socket.error:
            self.errors.append(_('Connection timed out'))
        except smtplib.SMTPServerDisconnected, exception:
            self.errors.append(_('The server disconnected abruptly'))
        except smtplib.SMTPSenderRefused, exception:
            self.errors.append(_('The sender %(sender)s was rejected') % {
            'sender': exception.sender})
        except smtplib.SMTPRecipientsRefused, exception:
            self.errors.append(_('Some recipients: %(recpts)s were'
            ' rejected with errors: %(errors)s') % {'recpts': str(exception),
            'errors': str(exception.recipients)})
        except smtplib.SMTPConnectError:
            self.errors.append(_('Error occured while establishing'
            ' connection to the server'))
        except smtplib.SMTPHeloError:
            self.errors.append(_('Server rejected our HELO message'))
        except smtplib.SMTPResponseException, exception:
            self.errors.append(_('Error occured, CODE:'
            ' %(code)s MESSAGE: %(msg)s') % {'code': exception.smtp_code})
        return False

    def ping(self, count=None):
        "ping host"
        if count is None:
            count = 5
        ping_cmd = ['ping', '-c', str(count), self.host]
        print ping_cmd
        pipe = Popen(ping_cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = pipe.communicate()
        if pipe.returncode == 0:
            return True
        else:
            self.errors.append(stderr)
            return False

    def setdebug(self):
        "enable debug info"
        self.debug = True

    def tests(self, pingcount=None):
        "Run all tests"
        if self.ping(pingcount) and self.smtp_test():
            return True
        return False

    def reset_errors(self):
        "reset errors"
        self.errors[:] = []
