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

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from baruwa.reports.views import pack_reportlib_data, Maillog
from baruwa.reports.graphs import drawPieGraph
from django.core.management.base import NoArgsCommand
from django.db.models import Count, Sum, Max, Min

def do_pdf(name,Elements):
    doc =  SimpleDocTemplate(name)
    doc.build(Elements)

def get_pie_data(query_field, order_by):
    kwargs = {}
    kw = '%s__exact' % query_field
    kwargs[kw] = ""
    data = Maillog.objects.values(query_field).\
        exclude(**kwargs).annotate(num_count=Count(query_field),size=Sum('size')).order_by(order_by)[:10]
    return pack_reportlib_data(data, query_field, order_by.lstrip('-'))


class Command(NoArgsCommand):
    help = "Generate traffic analysis reports"

    def handle_noargs(self, **options):
        styles =  getSampleStyleSheet()
        Title =  Paragraph("Baruwa mail traffic report", styles["Heading1"])
        Elements =  [Title]

        reports = [
                ('from_address','-num_count'),
                ('from_address','-size'),
                ('from_domain','-num_count'),
                ('from_domain','-size'),
                ('to_address','-num_count'),
                ('to_address','-size'),
                ('to_domain','-num_count'),
                ('to_domain','-size'),
                ('clientip','-num_count'),
            ]
        for report in reports:
            data = get_pie_data(report[0], report[1])
            graph = drawPieGraph(data, (350, 230), True)
            Elements.extend([graph])

        do_pdf('test.pdf', Elements)
