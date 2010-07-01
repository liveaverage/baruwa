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
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Generates an email report of the quarantined messages for the past 24 hours"

    def handle_noargs(self, **options):
        from django.template.loader import render_to_string
        from django.contrib.auth.models import User
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        from baruwa.messages.models import Message
        from baruwa.accounts.models import UserProfile, UserAddresses
        import datetime
        try:
            from django.forms.fields import email_re
        except ImportError:
            from django.core.validators import email_re


        tmp = UserProfile.objects.values('user').filter(send_report=1)
        ids = [ id['user'] for id in tmp ]
        users = User.objects.filter(id__in=ids)
        url = getattr(settings, 'QUARANTINE_REPORT_HOSTURL','')
        a_day = datetime.timedelta(days=1)
        yesterday = datetime.date.today() - a_day
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL','postmaster@localhost')
        print "=================== Processing quarantine notifications ======================"
        for user in users:
            if email_re.match(user.email) or email_re.match(user.username):  
                addresses = UserAddresses.objects.values('address').filter(user=user).exclude(enabled=0)
                account_type = UserProfile.objects.values('account_type').get(user=user)
                message_list = Message.quarantine_report.for_user(addresses, account_type).values('id','timestamp',
                    'from_address','to_address','subject','size','sascore','highspam','spam','virusinfected',
                    'otherinfected','whitelisted','blacklisted','nameinfected').exclude(timestamp__lt=yesterday).order_by('-sascore')[:25]
                html_content = render_to_string('messages/quarantine_report.html', {'items':message_list,'host_url':url})
                subject = 'Baruwa quarantine report for %s' % user.username
                if email_re.match(user.username):
                    to = user.username
                if email_re.match(user.email):
                    to = user.email

                if message_list:
                    text_content = render_to_string('messages/quarantine_report_text.html',{'items':message_list,'host_url':url})
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    print "sent quarantine report to "+to
                else:
                    print "skipping report to "+to+" no messages"
        print "=================== completed quarantine notifications ======================"
