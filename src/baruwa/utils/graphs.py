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

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor
from reportlab.lib import colors

PIE_COLORS = ['#FF0000', '#ffa07a', '#deb887', '#d2691e', '#008b8b',
            '#006400', '#ff8c00', '#ffd700', '#f0e68c', '#000000']
PIE_CHART_COLORS = [ HexColor(pie_color) for pie_color in PIE_COLORS ]

class MessageTotalsGraph(Drawing):
    "Draws a line graph"
    def __init__(self, width=600, height=250, *args, **kwargs):
        Drawing.__init__(self, width, height, *args, **kwargs)

        self.add(HorizontalLineChart(), name='chart')
        self.chart.x = 0
        self.chart.y = 0
        self.chart.height = 225
        self.chart.width = 500
        self.chart.joinedLines = 1
        self.chart.categoryAxis.categoryNames = ['']
        self.chart.categoryAxis.labels.boxAnchor = 'n'
        self.chart.valueAxis.valueMin = 0
        self.chart.valueAxis.valueMax = 60
        self.chart.valueAxis.valueStep = 15
        self.chart.lines[0].strokeWidth = 2
        self.chart.lines[1].strokeWidth = 2
        self.chart.lines[2].strokeWidth = 2
        self.chart.lines[0].strokeColor = colors.green
        self.chart.lines[1].strokeColor = colors.pink
        self.chart.lines[2].strokeColor = colors.red

class PieChart(Drawing):
    "Draws a pie chart"
    def __init__(self, width=100, height=100, *args, **kwargs):
        Drawing.__init__(self, width, height, *args, **kwargs)
        self.add(Pie(), name='chart')

        for i in range(10):
            self.chart.slices[i].fillColor = PIE_CHART_COLORS[i]
            self.chart.slices[i].labelRadius = 1.4
            self.chart.slices[i].fontName = 'Helvetica'
            self.chart.slices[i].fontSize = 7

class BarChart(Drawing):
    "Draws a bar chart"
    def __init__(self, width=600, height=250, *args, **kwargs):
        Drawing.__init__(self, width, height, *args, **kwargs)

        self.add(VerticalBarChart(), name='chart')
        self.chart.x = 10
        self.chart.y = 10
        self.chart.width = 500
        self.chart.height = 225
        self.chart.strokeColor = None
        self.chart.valueAxis.valueMin = 0
        #self.chart.valueAxis.valueMax = 50
        #self.chart.valueAxis.valueStep = 10
        self.chart.data = [(1, 2, 5),]
        self.chart.categoryAxis.visible = 1
        self.chart.bars[0].fillColor = colors.green
        self.chart.bars[1].fillColor = colors.pink
        self.chart.bars[2].fillColor = colors.red
        self.chart.categoryAxis.categoryNames = ['']#labels
