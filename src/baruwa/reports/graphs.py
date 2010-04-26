def drawSVGPie(data, size):
    "Draws an svg pie graph"

    import math
    from xml.dom.minidom import Document

    sum = 0
    for item in data:
        sum += item['y']

    max = len(data)
    deg = sum / 360
    jun = sum / 2
    cx = size[0] / 2
    cy = size[1] / 2
    radius = (min(cx, cy) - 30)
    dx = radius
    dy = 0
    oldangle = 0
    
    svg = Document()
    root = svg.createElement('svg')
    root.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    root.setAttribute('xmlns:svg', 'http://www.w3.org/2000/svg')
    root.setAttribute('width', str(size[0]))
    root.setAttribute('height', str(size[1]))
    root.setAttribute('id', 'svg2')
    root.setAttribute('version', '1.0')
    svg.appendChild(root)
    rect = svg.createElement('rect')
    rect.setAttribute('fill', 'white')
    rect.setAttribute('fill-opacity', '1')
    rect.setAttribute('fill-rule', 'evenodd')
    rect.setAttribute('stroke', 'none')
    rect.setAttribute('stroke-opacity', '0')
    rect.setAttribute('stroke-width', '1')
    rect.setAttribute('stroke-linecap', 'butt')
    rect.setAttribute('stroke-linejoin', 'miter')
    rect.setAttribute('stroke-miterlimit', '4')
    rect.setAttribute('x', '10')
    rect.setAttribute('y', '10')
    rect.setAttribute('width', str(size[0]))
    rect.setAttribute('height', str(size[1]))
    root.appendChild(rect)
    g = svg.createElement('g')
    root.appendChild(g)

    for n in range (max):
        angle = oldangle + data[n]['y'] / deg
        x = math.cos(math.radians(angle)) * radius
        y = math.sin(math.radians(angle)) * radius
        if data[n]['y'] > jun:
            laf = 1
        else:
            laf = 0
        ax = cx + x
        ay = cy + y
        adx = cx + dx
        ady = cy + dy
        path = svg.createElement('path') 
        path.setAttribute('d', 'M%s,%s L%s,%s A%s,%s 0 %s,1 %s,%sZ' % (cx, cy, adx, ady, radius, radius, laf, ax, ay))
        path.setAttribute('fill', data[n]['color'])
        path.setAttribute('fill-opacity', '1')
        path.setAttribute('fill-rule', 'evenodd')
        path.setAttribute('stroke', 'black')
        path.setAttribute('stroke-opacity', '1')
        path.setAttribute('stroke-width', '1')
        path.setAttribute('stroke-linecap', 'butt')
        path.setAttribute('stroke-linejoin', 'miter')
        path.setAttribute('stroke-miterlimit', '4')
        path.setAttribute('stroke-dasharray', 'none')
        g.appendChild(path)
        dx = x
        dy = y
        oldangle = angle
    return svg.toprettyxml(encoding='utf-8')

from reportlab.graphics.shapes import Drawing

def drawBarGraph(data, size, is_sa=False):
    "Generates a dynamic Bar chart"

    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib import colors

    bc = VerticalBarChart()
    bc.x, bc.y = 30, 5
    bc.width, bc.height = (size[0] - 20, size[1] - 20)
    bc.strokeColor = None

    bc.data = data
    bc.categoryAxis.visible = 1
    if not is_sa:
        bc.bars[0].fillColor = colors.green
        bc.bars[1].fillColor = colors.pink
        bc.bars[2].fillColor = colors.red
        bc.valueAxis.valueStep = 100
    else:
        bc.bars[0].fillColor = colors.blue
        bc.valueAxis.valueStep = 500
        #bc.barLabelFormat = '%d'
        #bc.barLabels.nudge = 10
        bc.categoryAxis.categoryNames = map(str, data[0])
        bc.categoryAxis.labels.dx = -1
        bc.categoryAxis.labels.dy = -12
        bc.categoryAxis.visibleTicks = 1
        bc.categoryAxis.labels.angle = 90
        bc.y = 20
    drawing = Drawing(size[0], size[1])
    drawing.add(bc)
    img = drawing.asString('png')
    return img

def drawPieGraph(data, size):
    "Generates a dynamic Pie chart"

    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.colors import HexColor
    from baruwa.reports.views import pie_colors

    pie_chart_colors = [ HexColor(hex) for hex in pie_colors ]
    
    pc = Pie()
    w = min(size) - 55
    pc.width, pc.height = w, w
    r = (w / 2)
    pc.x, pc.y = r, 23
    pc.data = data[0]
    pc.labels = data[1]
    pc.slices.fontName = 'Helvetica-Bold'
    pc.simpleLabels = 1
    pc.slices.strokeWidth = 1

    m = len(pie_chart_colors)
    n = len(data[0])
    i = m // n
    for j in xrange(n):
        setattr(pc.slices[j], 'fillColor', pie_chart_colors[j * i % m])

    drawing = Drawing(size[0], size[1])
    drawing.add(pc)
    img = drawing.asString('png')
    return img
