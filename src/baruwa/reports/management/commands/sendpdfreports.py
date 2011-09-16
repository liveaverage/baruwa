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

import re
import datetime

from optparse import make_option
from StringIO import StringIO

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Rect
from reportlab.graphics.shapes import Drawing
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, \
TableStyle, Paragraph, Image, PageBreak
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.contrib.auth.models import User
from django.core.validators import email_re
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.template.defaultfilters import filesizeformat
from django.core.mail import EmailMessage, SMTPConnection
from django.core.management.base import BaseCommand, CommandError

from baruwa.messages.models import Message
from baruwa.messages.models import MessageTotals
from baruwa.accounts.models import UserProfile, UserAddresses
from baruwa.messages.templatetags.messages_extras import tds_trunc
from baruwa.utils.graphs import PieChart, PIE_CHART_COLORS, BarChart


def draw_square(color):
    "draws a square"

    square = Drawing(5, 5)
    sqr = Rect(0, 2.5, 5, 5)
    sqr.fillColor = color
    sqr.strokeColor = color
    square.add(sqr)
    return square

def checkdate(date):
    "check a date string"
    year, month, day = map(int, date.split('-'))
    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False


class Command(BaseCommand):
    "Generate and email PDF reports"
    help = _("Generates and sends PDF summary reports via email")
    option_list = BaseCommand.option_list + (
        make_option('--bydomain', action='store_true', dest='by_domain',
            default=False, help='Generate reports per domain'),
        make_option('--domain', dest='domain_name', default='all',
            help='Specify the domain to report on, use "all" for all the domains'),
        make_option('--copyadmin', action='store_true', dest='copy_admin',
            default=False, help='Send a copy of the report to the admin'),
        make_option('--period', dest='period', default=None,
            help='Period to report on: valid options are '
                '"day(s)","week(s)"" Examples: '
                '--period="1 day" --period="2 weeks"'),
        make_option('--full', action='store_true', dest='include_daily',
            default=False, help='Include the daily totals table'),
        make_option('--startdate', dest='startdate', default=None,
            help='Start date to report on: YYYY-MM-DD'),
        make_option('--enddate', dest='enddate', default=None,
            help='End date to report on: YYYY-MM-DD'),
    )

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError(_("Command doesn't accept any arguments"))

        by_domain = options.get('by_domain')
        domain_name = options.get('domain_name')
        copy_admin = options.get('copy_admin')
        period = options.get('period')
        include_daily = options.get('include_daily')
        startdate =  options.get('startdate')
        end_date =  options.get('enddate')
        enddate = None

        if startdate and end_date:
            if not checkdate(startdate) or not checkdate(end_date):
                raise CommandError(_("The startdate, enddate specified is invalid"))
            daterange = (startdate, end_date)
        else:
            daterange = None

        period_re = re.compile(r"(?P<num>(\d+))\s+(?P<period>(day|week|month))(?:s)?")
        if period:
            match = period_re.match(period)
            if not match:
                raise CommandError(_("The period you specified is invalid"))
            num = match.group('num')
            ptype = match.group('period')
            if not ptype.endswith('s'):
                ptype = ptype + 's'
            delta = datetime.timedelta(**{ptype: int(num)})
            enddate = datetime.date.today() - delta

        table_style = TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.15, colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (4, 1), (-1, -1), 'MIDDLE'),
            ('SPAN', (4, 1), (-1, -1)),
        ])

        styles = getSampleStyleSheet()

        reports = [
            [
                'from_address', {'from_address__exact': ""}, 'num_count',
                'Top senders by quantity'],
            [
                'from_address', {'from_address__exact': ""}, 'total_size',
                'Top senders by volume'],
            [
                'from_domain', {'from_domain__exact': ""}, 'num_count',
                'Top sender domains by quantity'],
            [
                'from_domain', {'from_domain__exact': ""}, 'total_size',
                'Top sender domains by volume'],
            [
                'to_address', {'to_address__exact': ""}, 'num_count',
                'Top recipients by quantity'],
            [
                'to_address', {'to_address__exact': ""}, 'total_size',
                'Top recipients by volume'],
            [
                'to_domain', {'to_domain__exact': "",
                'to_domain__isnull': False}, 'num_count',
                'Top recipient domains by quantity'],
            [
                'to_domain', {'to_domain__exact': "",
                'to_domain__isnull': False}, 'total_size',
                'Top recipient domains by volume'],
        ]

        emails = []
        admin_addrs = []
        if copy_admin:
            mails = User.objects.values('email').filter(is_superuser=True)
            admin_addrs = [mail['email'] for mail in mails]

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL',
            'postmaster@localhost')
        url = getattr(settings, 'QUARANTINE_REPORT_HOSTURL', '')
        logo_dir = getattr(settings, 'MEDIA_ROOT', '')
        img = Image(logo_dir + '/imgs/css/logo.jpg')

        def build_chart(data, column, order, title):
            "build chart"
            headings = [('', _('Address'), _('Count'), _('Volume'), '')]
            rows = [[draw_square(PIE_CHART_COLORS[index]),
            tds_trunc(row[column], 45), row['num_count'],
            filesizeformat(row['total_size']), '']
            for index, row in enumerate(data)]

            if len(rows) != 10:
                missing = 10 - len(rows)
                add_rows = [
                    ('', '', '', '', '') for ind in range(missing)
                    ]
                rows.extend(add_rows)

            headings.extend(rows)
            dat = [row[order] for row in data]
            total = sum(dat)
            labels = [
                    ("%.1f%%" % ((1.0 * row[order] / total) * 100))
                    for row in data
                ]

            pie = PieChart()
            pie.chart.labels = labels
            pie.chart.data = dat
            headings[1][4] = pie

            table_with_style = Table(headings, [0.2 * inch,
                2.8 * inch, 0.5 * inch, 0.7 * inch, 3.2 * inch])
            table_with_style.setStyle(table_style)

            paragraph = Paragraph(title, styles['Heading1'])

            return [paragraph, table_with_style]

        def build_parts(account, enddate, isdom=None, daterange=None):
            "build parts"
            parts = []
            sentry = 0
            for report in reports:
                column = report[0]
                exclude_kwargs = report[1]
                order_by = "-%s" % report[2]
                order = report[2]
                title = report[3]

                if isdom:
                    #dom
                    data = Message.objects.values(column).\
                    filter(Q(from_domain=account.address) | \
                    Q(to_domain=account.address)).\
                    exclude(**exclude_kwargs).annotate(
                        num_count=Count(column), total_size=Sum('size')
                    ).order_by(order_by)
                    if daterange:
                        data.filter(date__range=(daterange[0], daterange[1]))
                    elif enddate:
                        data.filter(date__gt=enddate)
                    data = data[:10]
                else:
                    #all users
                    data = Message.report.all(user, enddate, daterange).values(
                            column).exclude(**exclude_kwargs).annotate(
                            num_count=Count(column), total_size=Sum('size')
                            ).order_by(order_by)
                    data = data[:10]

                if data:
                    sentry += 1
                    pgraphs = build_chart(data, column, order, title)
                    parts.extend(pgraphs)
                    parts.append(Spacer(1, 70))
                    if (sentry % 2) == 0:
                        parts.append(PageBreak())
            parts.append(Paragraph(_('Message Totals'), styles['Heading1']))
            if isdom:
                #doms
                msg_totals = MessageTotals.objects.doms(account.address, enddate)
            else:
                #norm
                filters = []
                addrs = [
                    addr.address for addr in UserAddresses.objects.filter(
                        user=account
                    ).exclude(enabled__exact=0)]
                if enddate:
                    efilter = {
                                'filter': 3,
                                'field': 'date',
                                'value': str(enddate)
                               }
                    filters.append(efilter)
                msg_totals = MessageTotals.objects.all(
                                account, filters, addrs,
                                profile.account_type,
                                daterange)

            mail_total = []
            spam_total = []
            virus_total = []
            dates = []
            if include_daily:
                rows = [(
                Table([[draw_square(colors.white),
                Paragraph('Date', styles["Heading6"])]],
                [0.35 * inch, 1.50 * inch, ]),
                Table([[draw_square(colors.green),
                Paragraph('Mail totals', styles["Heading6"])]],
                [0.35 * inch, 1.50 * inch, ]),
                Table([[draw_square(colors.pink),
                Paragraph('Spam totals', styles["Heading6"])]],
                [0.35 * inch, 1.50 * inch, ]),
                Table([[draw_square(colors.red),
                Paragraph('Virus totals', styles["Heading6"])]],
                [0.35 * inch, 1.50 * inch, ]),
                )]
            for ind, msgt in enumerate(msg_totals):
                if ind % 10:
                    dates.append('')
                else:
                    dates.append(str(msgt.date))

                mail_total.append(int(msgt.mail_total))
                spam_total.append(int(msgt.spam_total))
                virus_total.append(int(msgt.virus_total))
                if include_daily:
                    rows.append((str(msgt.date), msgt.mail_total,
                    msgt.spam_total, msgt.virus_total))

            graph = BarChart()
            graph.chart.data = [
                    tuple(mail_total), tuple(spam_total),
                    tuple(virus_total)
                ]
            graph.chart.categoryAxis.categoryNames = dates
            graph_table = Table([[graph]], [7.4 * inch])
            parts.append(graph_table)
            if include_daily:
                rows.append(('Totals', sum(mail_total), sum(spam_total),
                sum(virus_total)))
                parts.append(Spacer(1, 20))
                graph_table = Table(rows, [1.85 * inch, 1.85 * inch,
                1.85 * inch, 1.85 * inch, ])
                graph_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.15, colors.black),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
                #('BACKGROUND', (0, -1), (-1, -1), colors.green),
                ]))
                parts.append(graph_table)
            return parts

        def build_pdf(charts):
            "Build a PDF"
            pdf = StringIO()
            doc = SimpleDocTemplate(pdf, topMargin=50, bottomMargin=18)
            logo = [(img, _('Baruwa mail report'))]
            logo_table = Table(logo, [2.0 * inch, 5.4 * inch])
            logo_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
            ('FONTSIZE', (1, 0), (-1, 0), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.15, colors.black),
            ]))
            parts = [logo_table]
            parts.append(Spacer(1, 20))
            parts.extend(charts)
            try:
                doc.build(parts)
            except IndexError:
                pass
            return pdf

        def gen_email(pdf, user, owner):
            "generate and return email"
            text_content = render_to_string('reports/pdf_report.txt',
                {'user': user, 'url': url})
            subject = _('Baruwa usage report for: %(user)s') % {
                        'user': owner}
            if email_re.match(user.username):
                toaddr = user.username
            if email_re.match(user.email):
                toaddr = user.email

            if admin_addrs:
                msg = EmailMessage(subject, text_content, from_email, [toaddr], admin_addrs)
            else:
                msg = EmailMessage(subject, text_content, from_email, [toaddr])
            msg.attach('baruwa.pdf', pdf.getvalue(), "application/pdf")
            print _("* Queue %(user)s's report to: %(addr)s") % {
                'user': owner, 'addr': toaddr}
            pdf.close()
            return msg

        print _("=================== Processing reports ======================")
        if by_domain:
            #do domain query
            #print "camacamlilone"
            domains = UserAddresses.objects.filter(Q(enabled=1), Q(address_type=1))
            if domain_name != 'all':
                domains = domains.filter(address=domain_name)
                if not domains:
                    print _("========== domain name %(dom)s does not exist ==========") % {
                    'dom': domain_name
                    }
            for domain in domains:
                if email_re.match(domain.user.email):
                    parts = build_parts(domain, enddate, True, daterange)
                    if parts:
                        pdf = build_pdf(parts)
                        email = gen_email(pdf, domain.user, domain.address)
                        emails.append(email)
        else:
            #do normal query
            profiles = UserProfile.objects.filter(send_report=1)
            for profile in profiles:
                try:
                    user = profile.user
                    if email_re.match(user.email) or email_re.match(user.username):
                        parts = build_parts(user, enddate, False, daterange)
                        if parts:
                            pdf = build_pdf(parts)
                            email = gen_email(pdf, user, user.username)
                            emails.append(email)
                except User.DoesNotExist:
                    pass

        if emails:
            try:
                conn = SMTPConnection()
                conn.send_messages(emails)
                print _("====== sending %(num)s messages =======") % {
                        'num': str(len(emails))}
            except Exception, exception:
                print _("Sending failed ERROR: %(error)s") % {'error': str(exception)}
