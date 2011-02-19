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

from email.Header import decode_header
from lxml.html.clean import Cleaner
import re, codecs

NOTFOUND = object()
UNCLEANTAGS = ['html', 'head', 'link', 'img', 'a', 'body']

class EmailParser(object):
    """
    Parses a email message
    """

    def process_headers(self, msg):
        "Populate the headers"
        headers = {}
        headers['subject'] = self.get_header(msg['Subject'])
        headers['to'] = self.get_header(msg['To'])
        headers['from'] = self.get_header(msg['From'])
        headers['date'] = self.get_header(msg['Date'])
        #headers['message-id'] = self.get_header(msg['Message-ID'])
        return headers

    def get_header(self, header_text, default="ascii"):
        "Decode and return the header"
        if not header_text:
            return header_text

        header_sections = []
        try:
            headers = decode_header(header_text)
            header_sections = [ unicode(text, charset or default)
                                for text, charset in headers ]
        except:
            pass
        return u"".join(header_sections)

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
        #headers = self.process_headers(msg)
        #filename = "%s.txt" % headers['message-id']
        content_type = msg.get_content_type()
        return dict(filename='rfc822.txt', content_type=content_type)

    def process_msg(self, message, parts, attachments):
        "Recursive message processing"
        
        content_type = message.get_content_type()
        attachment = message.get_param('attachment',
                    NOTFOUND, 'Content-Disposition')
        if content_type == 'message/rfc822':
            [ attachments.append(self.parse_attached_msg(msg))
                for msg in message.get_payload() ]
            return True

        if message.is_multipart():
            if content_type == 'multipart/alternative':
                for par in reversed(message.get_payload()):
                    if self.process_msg(par, parts, attachments):
                        return True
            else:
                [ self.process_msg(par, parts, attachments)
                    for par in message.get_payload() ]
            return True
        success = False

        if (content_type == 'text/html'
            and attachment is NOTFOUND):
            parts.append({'type':'html',
                'content':self.return_html_part(message)})
            success = True
        elif (content_type.startswith('text/')
                and attachment is NOTFOUND):
            parts.append({'type':'text',
                'content':self.return_text_part(message)})
            success = True
        filename = message.get_filename(None)
        if filename and not attachment is NOTFOUND:
            attachments.append(
                dict(filename=filename, content_type=content_type))
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
        return self.sanitize_html(body.decode(charset, 'replace'))

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
                    filename = re.sub(r"\s", "_", filename)
                    num += 1
                if attach_id == num:
                    from StringIO import StringIO
                    if part.is_multipart():
                        data = part.as_string()
                    else:
                        data = part.get_payload(decode=True)
                    attachment  = StringIO(data)
                    attachment.content_type =  part.get_content_type()
                    attachment.size = len(data)
                    attachment.name = filename
                    return attachment
        return None
        
    def sanitize_html(self, msg):
        "Clean up html"
        cleaner = Cleaner(style = True, remove_tags=UNCLEANTAGS)
        return cleaner.clean_html(msg)

        
