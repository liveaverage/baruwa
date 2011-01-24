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

"Messages tasks"

from celery.task import Task
from django.utils.translation import ugettext as _
from baruwa.messages.models import Message
from baruwa.utils.mail.message import ProcessQuarantinedMessage


class ProcessQuarantine(Task):
    "Process quarantine"
    name = 'process-quarantine'
    serializer = 'json'

    def run(self, job, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        logger.info(_("Bulk Processing %(len)d quarantined messages"),
            {'len': len(job['message_id'])})

        query = Message.objects.values('id', 'date', 'from_address',
            'to_address').filter(id__in=job['message_id'])
        messages = dict([(item['id'], [str(item['date']),
                    item['from_address'], item['to_address']])
                    for item in query])
        results = []

        for index, msgid in enumerate(job['message_id']):
            self.update_state(kwargs["task_id"], "PROGRESS",
            {'current': index, 'total': len(job['message_id'])})
            result = {'message_id': msgid, 'release': None, 'learn': None,
                'delete': None, 'errors': []}
            try:
                processor = ProcessQuarantinedMessage(msgid,
                            messages[msgid][0])
            except AssertionError, exception:
                for task in ['release', 'learn', 'todelete']:
                    if job[task]:
                        if task == 'todelete':
                            task = 'delete'
                        result[task] = False
                        result['errors'].append((task, str(exception)))
                        logger.info(_("Message: %(msgid)s %(task)s failed with "
                        "error: %(error)s"), {'msgid': msgid, 'task': task,
                        'error': str(exception)})
                results.append(result)
                continue
            if job['release']:
                if messages[msgid][1]:
                    if job['use_alt']:
                        to_addrs = job['altrecipients'].split(',')
                    else:
                        to_addrs = messages[msgid][2].split(',')
                    result['release'] = processor.release(messages[msgid][1],
                                        to_addrs)
                    if not result['release']:
                        error = ' '.join(processor.errors)
                        result['errors'].append(('release', error))
                        processor.reset_errors()
                    else:
                        logger.info(_("Message: %(msgid)s released to: %(to)s"),
                        {'msgid': msgid, 'to': ' '.join(to_addrs)})
                else:
                    result['release'] = False
                    error = _('The sender address is empty')
                    result['errors'].append(('release', error))
                    logger.info(_("Message: %(msgid)s release failed with "
                    "error: %(error)s"), {'error': error})
            if job['learn']:
                result['learn'] = processor.learn(job['salearn_as'])
                if not result['learn']:
                    error = ' '.join(processor.errors)
                    result['errors'].append(('learn', error))
                    processor.reset_errors()
                    logger.info(_("Message: %(msgid)s learning failed with "
                    "error: %(error)s"), {'error': error})
                else:
                    logger.info(_("Message: %(msgid)s learnt as %(learn)s"),
                    {'msgid': msgid, 'learn': job['salearn_as']})
            if job['todelete']:
                result['delete'] = processor.delete()
                if not result['delete']:
                    error = ' '.join(processor.errors)
                    result['errors'].append(('delete', error))
                    processor.reset_errors()
                    logger.info(_("Message: %(msgid)s deleting failed with "
                    "error: %(error)s"), {'error': error})
                else:
                    logger.info(_("Message: %(msgid)s deleted from quarantine"))
            results.append(result)
        return results
