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
from baruwa.utils.mail.message import ProcessQuarantinedMessage, PreviewMessage


class ReleaseMessage(Task):
    "Release message"
    name = 'release-message'
    serializer = 'json'

    def run(self, messageid, date, from_addr, to_addr, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        try:
            processor = ProcessQuarantinedMessage(messageid, date)
        except AssertionError, error:
            return {'success': False, 'error': error}
        if processor.release(from_addr, to_addr):
            logger.info(_("Message: %(id)s released to: %(addrs)s"),
            {'id': messageid, 'addrs': ','.join(to_addr)})
            return {'success': True, 'error': ''}
        else:
            logger.info(_("Message: %(id)s release failed"),
            {'id': messageid})
            return {'success': False, 'error': ' '.join(processor.errors)}


class ProcessQuarantinedMsg(Task):
    "Process quarantined message"
    name = 'process-quarantined-msg'
    serializer = 'json'

    def run(self, *args, **kwargs):
        'run da ting'
        job = args[0]
        logger = self.get_logger(**kwargs)
        logger.info(_('Processing quarantined message: %(id)s'),
        dict(id=job['message_id']))
        result = dict(message_id=job['message_id'], release=None,
        learn=None, delete=None, errors=[])

        try:
            processor = ProcessQuarantinedMessage(job['message_id'],
                        job['date'])
        except AssertionError, exception:
            for task in ['release', 'learn', 'todelete']:
                if job[task]:
                    if task == 'todelete':
                        task = 'delete'
                    result[task] = False
                    result['errors'].append((task, str(exception)))
                    logger.info(_("Message: %(msgid)s %(task)s failed with "
                    "error: %(error)s"), dict(msgid=job['message_id'],
                    task=task, error=str(exception)))
            return result
        if job['release']:
            if job['from_address']:
                if job['use_alt']:
                    to_addrs = job['altrecipients'].split(',')
                else:
                    to_addrs = job['to_address'].split(',')
                result['release'] = processor.release(job['from_address'],
                to_addrs)
                if not result['release']:
                    error = ' '.join(processor.errors)
                    result['errors'].append(('release', error))
                    processor.reset_errors()
                else:
                    logger.info(_("Message: %(msgid)s released to: %(to)s"),
                    dict(msgid=job['message_id'], to=', '.join(to_addrs)))
            else:
                result['release'] = False
                error = _('The sender address is empty')
                result['errors'].append(('release', error))
                logger.info(_("Message: %(msgid)s release failed with "
                "error: %(error)s"), dict(msgid=job['message_id'],
                error=error))
        if job['learn']:
            result['learn'] = processor.learn(job['salearn_as'])
            if not result['learn']:
                error = ' '.join(processor.errors)
                result['errors'].append(('learn', error))
                processor.reset_errors()
                logger.info(_("Message: %(msgid)s learning failed with "
                "error: %(error)s"), dict(msgid=job['message_id'],
                error=error))
            else:
                logger.info(_("Message: %(msgid)s learnt as %(learn)s"),
                dict(msgid=job['message_id'], learn=job['salearn_as']))
        if job['todelete']:
            result['delete'] = processor.delete()
            if not result['delete']:
                error = ' '.join(processor.errors)
                result['errors'].append(('delete', error))
                processor.reset_errors()
                logger.info(_("Message: %(msgid)s deleting failed with "
                "error: %(error)s"), dict(msgid=job['message_id'],
                error=error))
            else:
                logger.info(_("Message: %(msgid)s deleted from quarantine"),
                dict(msgid=job['message_id']))
                msg = Message.objects.get(pk=job['message_id'])
                msg.isquarantined = 0
                msg.save()
        return result


class ProcessQuarantine(Task):
    "Process quarantine"
    name = 'process-quarantine'
    serializer = 'json'

    def run(self, job, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        logger.info(_("Bulk Processing %(len)d quarantined messages"),
        dict(len=len(job['message_id'])))

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
                    "error: %(error)s"), {'msgid': msgid, 'error': error})
            if job['learn']:
                result['learn'] = processor.learn(job['salearn_as'])
                if not result['learn']:
                    error = ' '.join(processor.errors)
                    result['errors'].append(('learn', error))
                    processor.reset_errors()
                    logger.info(_("Message: %(msgid)s learning failed with "
                    "error: %(error)s"), {'msgid': msgid, 'error': error})
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
                    "error: %(error)s"), {'msgid': msgid, 'error': error})
                else:
                    logger.info(_("Message: %(msgid)s deleted from quarantine"),
                    {'msgid': msgid})
                    msg = Message.objects.get(pk=msgid)
                    msg.isquarantined = 0
                    msg.save()
            results.append(result)
        return results


class PreviewMessageTask(Task):
    "Preview message"
    name = 'preview-message'
    serializer = 'json'

    def run(self, messageid, date, attachid=None, **kwargs):
        "run"
        logger = self.get_logger(**kwargs)
        try:
            previewer = PreviewMessage(messageid, date)
        except AssertionError, error:
            logger.info(_("Accessing message: %(id)s, Failed: %(error)s"),
            {'id': messageid, 'error': error})
            return None
        if attachid:
            logger.info(_("Download attachment: %(attachid)s of message: %(id)s "
            "by user: %(user)s"), {'id': messageid, 'attachid': '', 'user': ''})
            return previewer.attachment(attachid)
        logger.info(_("Preview of message: %(id)s requested by user: %(user)s"),
        {'id': messageid, 'user': ''})
        return previewer.preview()
