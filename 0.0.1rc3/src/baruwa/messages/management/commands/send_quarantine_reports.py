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
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Generates an email report of the quarantined messages for the past 24 hours"

    def handle_noargs(self, **options):
        from django.template.loader import render_to_string
        from baruwa.accounts.models import User, UserFilters
        from baruwa.messages.models import Maillog
        from baruwa.reports.views import user_filter
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        import datetime
        try:
            from django.forms.fields import email_re
        except ImportError:
            from django.core.validators import email_re


        users = User.objects.filter(quarantine_report__exact=1)
        url = getattr(settings, 'QUARANTINE_REPORT_HOSTURL','')
        a_day = datetime.timedelta(days=1)
        yesterday = datetime.date.today() - a_day
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL','postmaster@localhost')
        print "=================== Processing quarantine notifications ======================"
        for user in users:
            if email_re.match(user.quarantine_rcpt) or email_re.match(user.username):  
                addresses = UserFilters.objects.filter(username=user.username).exclude(active='N')
                message_list = Maillog.objects.values('id','timestamp','from_address','to_address','subject','size','sascore','ishighspam','isspam'
                    ,'virusinfected','otherinfected','spamwhitelisted','spamblacklisted','nameinfected').filter(quarantined__exact=1).exclude(timestamp__lt=yesterday)
                message_list = user_filter(user,message_list,addresses,user.type)
                html_content = render_to_string('messages/quarantine_report.html', {'items':message_list,'host_url':url})
                subject = 'Baruwa quarantine report for %s' % user.username
                if email_re.match(user.username):
                    to = user.username
                if email_re.match(user.quarantine_rcpt):
                    to = user.quarantine_rcpt

                if message_list:
                    text_content = render_to_string('messages/quarantine_report_text.html',{'items':message_list,'host_url':url})
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    print "sent quarantine report to "+to
                else:
                    print "skipping report to "+to+" no messages"
        print "=================== completed quarantine notifications ======================"
