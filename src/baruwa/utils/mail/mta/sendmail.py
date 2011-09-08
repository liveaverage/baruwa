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

"Sendmail queue parser"
import codecs
#import fcntl
import re
import os
import subprocess

from datetime import datetime
from email.Header import decode_header

SUBJECT_RE = re.compile(r'^H(?:.+)?Subject:\s(.+)')


class QueueParser(object):
    "Sendmail queue parser"

    def __init__(self, queue):
        "init"
        self.qdir = queue
        self.items = []

    def delete(self, items):
        "delete queue items"
        done = []
        for item in items:
            hdr = "qf%s" % item
            dat = "df%s" % item
            data = os.path.join(self.qdir, dat)
            header = os.path.join(self.qdir, hdr)
            if os.path.exists(header) and os.path.exists(data):
                try:
                    os.remove(header)
                    os.remove(data)
                    done.append({'msgid': item, 'done': True})
                except OSError:
                    done.append({'msgid': item, 'done': False})
            else:
                done.append({'msgid': item, 'done': False})
        return done

    def process(self):
        "process"
        def getqfs(matched, dirname, files):
            "utility to get qf files"
            matched.extend([os.path.join(dirname, filename)
                            for filename in files
                            if filename.startswith('qf')])

        def extractinfo(qf):
            "extract attribs from qf file"
            try:
                qfile = codecs.open(qf, 'r', 'utf-8', 'replace')
                #fcntl.flock(qfile, fcntl.LOCK_EX)
                lines = qfile.readlines()
                #fcntl.flock(qfile, fcntl.LOCK_UN)
                qfile.close()
                attribs = {}
                attribs['to_address'] = []
                pipe1 = subprocess.Popen('hostname', shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                attribs['hostname'] = pipe1.stdout.read().strip()
                qid = os.path.basename(qf)
                attribs['messageid'] = qid[2:]
                attribs['size'] = 1
                dirpath = os.path.dirname(qf)
                possibles = []
                possibles.append(os.path.join(dirpath,
                                'df' + attribs['messageid']))
                possibles.append(os.path.join(dirpath.replace('qf', 'df'),
                                'df' + attribs['messageid']))
                for path in possibles:
                    if os.path.exists(path):
                        attribs['size'] = (os.path.getsize(path) +
                                            os.path.getsize(qf))
                        break
                attribs['subject'] = ''
                for line in lines:
                    if line.startswith('T'):
                        timestamp = str(datetime.fromtimestamp(float(line[1:])))
                        attribs['timestamp'] = timestamp
                        attribs['lastattempt'] = timestamp
                        continue
                    if line.startswith('S'):
                        attribs['from_address'] = line[1:-1].strip()
                        if not '@' in attribs['from_address']:
                            addr = "%s@%s" % (attribs['from_address'],
                                                attribs['hostname'])
                            attribs['from_address'] = addr
                        continue
                    if line.startswith('R'):
                        attribs['to_address'].append(
                        line[line.index(':') + 1:].strip())
                        continue
                    if line.startswith('N'):
                        attribs['attempts'] = line[1:].strip()
                        continue
                    if line.startswith('M'):
                        attribs['reason'] = line[1:].strip()
                        continue
                    if line.startswith('K'):
                        if float(line[1:]) > 0:
                            attempt = str(datetime.fromtimestamp(float(line[1:])))
                            attribs['lastattempt'] = attempt
                        continue
                    match = SUBJECT_RE.match(line)
                    if match:
                        subj = match.groups()[0].strip()
                        if subj.startswith('?='):
                            text, charset = decode_header(subj)[0]
                            subj = unicode(text, charset or 'ascii', 'replace')
                        attribs['subject'] = subj
                        break
                if attribs['from_address'] == '':
                    attribs['from_address'] = '<>'
                return attribs
            except (os.error, IOError):
                return None

        queuefiles = []
        os.path.walk(self.qdir, getqfs, queuefiles)
        results = [extractinfo(path) for path in queuefiles]
        self.items = [result for result in results if not result is None]
        return self.items
