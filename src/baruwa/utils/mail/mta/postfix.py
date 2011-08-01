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

"Postfix queue parser"
import os
import re
import time
import glob
import codecs
import datetime
import subprocess

from stat import ST_MTIME, ST_CTIME
from email.Header import decode_header

SUBJECT_RE = re.compile(r'^Subject:(.+)')


class QueueParser(object):
    "Postfix queue parser"

    def __init__(self, queue):
        "init"
        self.qdir = queue
        self.items = []

    def delete(self, items):
        "delete from queue"
        done = []
        for item in items:
            qfile = os.path.join(self.qdir, item)
            if os.path.exists(qfile):
                try:
                    os.remove(qfile)
                    done.append({'msgid': item, 'done': True})
                except OSError:
                    done.append({'msgid': item, 'done': False})
            else:
                done.append({'msgid': item, 'done': False})
        return done

    def process(self):
        "process"
        cmd = 'postconf -d queue_directory'
        try:
            from django.conf import settings
            confdir = getattr(settings, 'POSTFIX_ALT_CONF', None)
            if confdir and os.path.isdir(confdir):
                cmd = 'postconf -c %s -d queue_directory' % confdir
        except ImportError:
            pass
        postqdir = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            postqueuedir = postqdir.stdout.read().split()[2]
        except IndexError:
            postqueuedir = '/var/spool/postfix'

        def getqfs(matched, dirname, files):
            "process qf"
            matched.extend([os.path.join(dirname, filename)
                            for filename in files])

        def extractinfo(qf):
            "extract info from qf"
            try:
                cmd = "postcat %s" % qf
                postcat = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                lines = postcat.stdout.readlines()
                attribs = {}
                pipe1 = subprocess.Popen('hostname', shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                attribs['hostname'] = pipe1.stdout.read().strip()
                attribs['messageid'] = os.path.basename(qf)
                attribs['to_address'] = []
                attribs['attempts'] = 1
                for line in lines:
                    if line.startswith('message_size:'):
                        attribs['size'] = line.split()[1]
                        continue
                    if line.startswith('message_arrival_time:'):
                        arrival = line[line.index(' '):]
                        attribs['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S",
                        time.strptime(arrival.strip(), "%a %b %d %H:%M:%S %Y"))
                        continue
                    if line.startswith('sender:'):
                        attribs['from_address'] = line.split()[1]
                        continue
                    if line.startswith('recipient:'):
                        attribs['to_address'].append(line.split()[1])
                        continue
                    if line.startswith('Subject:'):
                        match = SUBJECT_RE.match(line)
                        subj = match.groups()[0].strip()
                        if subj.startswith('?='):
                            text, charset = decode_header(subj)[0]
                            subj = unicode(text, charset or 'ascii', 'replace')
                        attribs['subject'] = subj
                        break
                # try and get time message was defered using the timestamp on the
                # defered log file
                searchpath = "%s/defer/*" % postqueuedir
                possibles = glob.glob(searchpath)
                reasons = []
                for path in possibles:
                    if os.path.isfile(os.path.join(path, attribs['messageid'])):
                        ts = os.stat(os.path.join(path, attribs['messageid']))[ST_MTIME]
                        cs = os.stat(os.path.join(path, attribs['messageid']))[ST_CTIME]
                        if ts > cs:
                            attribs['attempts'] += 1
                        attribs['lastattempt'] = str(datetime.datetime.fromtimestamp(ts))
                        logfile = codecs.open(os.path.join(path, attribs['messageid']),
                                    'r', 'utf-8', 'replace')
                        reasons = logfile.readlines()
                        logfile.close()
                        break
                if not 'lastattempt' in attribs:
                    attribs['lastattempt'] = attribs['timestamp']
                if 'from_address' not in attribs or attribs['from_address'] == '':
                    attribs['from_address'] = '<>'
                attribs['reason'] = '\n'.join(reasons)
                return attribs
            except (os.error, IOError, KeyError):
                return None

        queuefiles = []
        os.path.walk(self.qdir, getqfs, queuefiles)
        results = [extractinfo(path) for path in queuefiles]
        self.items = [result for result in results if not result is None]
        return self.items
