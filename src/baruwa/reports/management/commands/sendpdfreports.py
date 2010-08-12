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
#

from django.core.management.base import NoArgsCommand

def draw_square(color):
    "draws a square"
    from reportlab.graphics.shapes import Rect
    from reportlab.graphics.shapes import Drawing
    
    square = Drawing(5, 5)
    sqr = Rect(0, 2.5, 5, 5)
    sqr.fillColor = color
    sqr.strokeColor = color
    square.add(sqr)
    return square
    
class Command(NoArgsCommand):
    "Generate and email PDF reports"
    
    def handle_noargs(self, **options):
        from django.db.models import Count, Sum
        from django.template.defaultfilters import filesizeformat
        from django.core.mail import EmailMessage, SMTPConnection
        from django.conf import settings
        from django.template.loader import render_to_string
        from baruwa.accounts.models import UserProfile, UserAddresses
        from baruwa.messages.models import Message
        from baruwa.messages.templatetags.messages_extras import tds_trunc
        from baruwa.messages.models import MessageTotals
        from baruwa.utils.graphs import PieChart, PIE_CHART_COLORS, BarChart
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Spacer, Table, \
        TableStyle, Paragraph, Image, PageBreak
        
        try:
            from django.forms.fields import email_re
        except ImportError:
            from django.core.validators import email_re
        
        try:
            from cStringIO import StringIO
        except:
            from StringIO import StringIO
        
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
                'from_address', {'from_address__exact':""}, 'num_count', 
                'Top senders by quantity'],
            [
                'from_address', {'from_address__exact':""}, 'size', 
                'Top senders by volume'],
            [   
                'from_domain', {'from_domain__exact':""}, 'num_count', 
                'Top sender domains by quantity'],
            [   
                'from_domain', {'from_domain__exact':""}, 'size', 
                'Top sender domains by volume'],
            [   
                'to_address', {'to_address__exact':""}, 'num_count', 
                'Top recipients by quantity'],
            [
                'to_address', {'to_address__exact':""}, 'size', 
                'Top recipients by volume'],
            [
                'to_domain', {'to_domain__exact':"", 
                'to_domain__isnull':False}, 'num_count', 
                'Top recipient domains by quantity'],
            [
                'to_domain', {'to_domain__exact':"", 
                'to_domain__isnull':False}, 'size', 
                'Top recipient domains by volume'],
        ]
        
        emails = []
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 
            'postmaster@localhost')
        url = getattr(settings, 'QUARANTINE_REPORT_HOSTURL','')
        logo_dir = getattr(settings, 'MEDIA_ROOT', '')
        img = Image(logo_dir + '/imgs/css/logo.jpg')
        profiles = UserProfile.objects.filter(send_report=1)
        
        print "=================== Processing reports ======================"
       
        for profile in profiles:
            user = profile.user
            if email_re.match(user.email) or email_re.match(user.username):
                
                pdf = StringIO()
                
                doc = SimpleDocTemplate(pdf, topMargin=50, bottomMargin=18)
                logo = [(img, 'Baruwa mail report')]
                logo_table = Table(logo, [2.0 * inch, 5.4 * inch])
                logo_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
                ('FONTSIZE', (1, 0), (-1, 0), 10),
                ('LINEBELOW', (0, 0),(-1, -1), 0.15, colors.black),
                ]))
                parts = [logo_table]
                parts.append(Spacer(1, 20))
                sentry = 0
                for report in reports:
                    column = report[0]
                    exclude_kwargs = report[1]
                    order_by = "-%s" % report[2]
                    order = report[2]
                    title = report[3]
                    
                    data = Message.report.all(user).values(column).\
                    exclude(**exclude_kwargs).annotate(
                        num_count=Count(column), size=Sum('size')
                    ).order_by(order_by)[:10]
                
                    if data:
                        sentry += 1
                        headings = [('', 'Address', 'Count', 'Volume', '')]
                        rows = [[draw_square(PIE_CHART_COLORS[index]), 
                        tds_trunc(row[column], 45), row['num_count'], 
                        filesizeformat(row['size']),''] 
                        for index,row in enumerate(data)]
                    
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
                        
                        parts.append(paragraph)
                        parts.append(table_with_style)
                        parts.append(Spacer(1, 70))
                        if (sentry % 2) == 0:
                            parts.append(PageBreak())
                #
                parts.append(Paragraph('Message Totals', styles['Heading1']))
                addrs = [
                    addr.address for addr in UserAddresses.objects.filter(
                        user=user
                    ).exclude(enabled__exact=0)]
                
                msg_totals = MessageTotals.objects.all(
                    user, [], addrs, profile.account_type)
                mail_total = []
                spam_total = []
                virus_total = []
                dates = []
                for ind, msgt in enumerate(msg_totals):
                    if ind % 10:
                        dates.append('')
                    else:
                        dates.append(str(msgt.date))
                        
                    mail_total.append(int(msgt.mail_total))
                    spam_total.append(int(msgt.spam_total))
                    virus_total.append(int(msgt.virus_total))
                    
                #graph = MessageTotalsGraph()
                graph = BarChart()
                graph.chart.data = [
                        tuple(mail_total), tuple(spam_total), 
                        tuple(virus_total)
                    ]
                graph.chart.categoryAxis.categoryNames = dates
                graph_table = Table([[graph],], [7.4 * inch])
                parts.append(graph_table)
                
                if not sentry:
                    sentry += 1
                    
                if sentry:
                    doc.build(parts)
                    
                    text_content = render_to_string('reports/pdf_report.txt',
                        {'user':user, 'url':url})
                    subject = 'Baruwa usage report for: %s' % user.username
                    if email_re.match(user.username):
                        toaddr = user.username
                    if email_re.match(user.email):
                        toaddr = user.email
                        
                    msg = EmailMessage(subject, text_content, from_email, [toaddr])
                    msg.attach('baruwa.pdf', pdf.getvalue(), "application/pdf")
                    #msg.send()
                    emails.append(msg)
                    print "* Queue "+user.username+"'s report to: "+toaddr
                    pdf.close()
        if emails:
            conn = SMTPConnection()
            conn.send_messages(emails)
            print "====== sending "+str(len(emails))+" messages ======="


        