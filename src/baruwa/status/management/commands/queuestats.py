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

"Queue stats generator"
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from baruwa.utils.mail.mailq import Mailq
from baruwa.status.models import MailQueueItem
from baruwa.utils.misc import get_config_option


class Command(BaseCommand):
    "Read the items in the queue and populate DB"
    option_list = BaseCommand.option_list + (
        make_option('--mta', dest='mta', default='exim', help='MTA'),
    )

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError(_("Command doesn't accept any arguments"))

        mtas = ['exim', 'sendmail', 'postfix']
        mta = options.get('mta')
        if not mta in mtas:
            raise CommandError(_("Only the following %(mta)s "
                                "MTA's are supported") %
                                {mta: ' '.join(mtas)})

        def runquery(queue, direction, ids):
            "run querys"
            for item in queue:
                item['direction'] = direction
                if len(item['to_address']) == 1:
                    if item['messageid'] in ids:
                        mqitem = MailQueueItem.objects.get(
                                messageid=item['messageid'])
                        for key in ['attempts', 'lastattempt']:
                            setattr(mqitem, key, item[key])
                    else:
                        item['to_address'] = item['to_address'][0]
                        mqitem = MailQueueItem(**item)
                    mqitem.save()
                else:
                    addrs = item['to_address']
                    for addr in addrs:
                        item['to_address'] = addr
                        if item['messageid'] in ids:
                            mqitem = MailQueueItem.objects.filter(
                                    messageid=item['messageid'],
                                    to_address=item['to_address']).all()[0]
                            for key in ['attempts', 'lastattempt']:
                                setattr(mqitem, key, item[key])
                        else:
                            mqitem = MailQueueItem(**item)
                        mqitem.save()

        inqdir = get_config_option('IncomingQueueDir')
        outqdir = get_config_option('OutgoingQueueDir')

        inqueue = Mailq(mta, inqdir)
        print _("== Delete flaged queue items from the inbound queue ==")
        ditems = MailQueueItem.objects.values('messageid').filter(
        flag__gt=0, direction=1).all()
        inrm = inqueue.delete([item['messageid'] for item in ditems])
        MailQueueItem.objects.filter(messageid__in=[
        item['msgid'] for item in inrm]).delete()
        print _("== Deleted %(num)d items from the inbound queue ==") % {
        'num': len(inrm)}
        inqueue.process()

        outqueue = Mailq(mta, outqdir)
        print _("== Delete flaged queue items from the outbound queue ==")
        ditems = MailQueueItem.objects.values('messageid').filter(
        flag__gt=0, direction=2).all()
        outrm = outqueue.delete([item['messageid'] for item in ditems])
        MailQueueItem.objects.filter(messageid__in=[
        item['msgid'] for item in outrm]).delete()
        print _("== Deleted %(num)d items from the outbound queue ==") % {
        'num': len(outrm)}
        outqueue.process()

        allids = [item['messageid'] for item in inqueue]
        allids.extend([item['messageid'] for item in outqueue])
        dbids = [item['messageid']
                for item in MailQueueItem.objects.values('messageid').all()]
        remids = [item for item in dbids if not item in allids]
        preids = [item for item in dbids if not item in remids]

        if remids:
            print (_("== Deleting %(items)d queue items from DB ==") %
                    {'items': len(remids)})
            MailQueueItem.objects.filter(messageid__in=remids).delete()

        if inqueue:
            print (_("== Processing the inbound queue: %(queue)s with %(items)d items ==") %
                    {'queue': inqdir, 'items': len(inqueue)})
            runquery(inqueue, 1, preids)
        else:
            print _("== Skipping the inbound queue 0 items found ==")
        if outqueue:
            print (_("== Processing the outbound queue: %(queue)s with %(items)d items ==") %
                    {'queue': outqdir, 'items': len(outqueue)})
            runquery(outqueue, 2, preids)
        else:
            print _("== Skipping the outbound queue 0 items found ==")
