# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.graphics.charts.piecharts import Pie3d
from reportlab.graphics.charts.barcharts import VerticalBarChart3D
from reportlab.graphics.charts.legends import Legend
from reportlab.lib import colors
from reportlab.lib.validators import Auto


CHART_COLORS = [
    colors.navy,
    colors.darkred,
    colors.olive,
    colors.mediumpurple,
    colors.cyan,
    colors.green,
    colors.red,
    colors.blue,
    colors.pink,
    colors.yellow,
]
DATA_PIE = [
    (39.0, 'Schnittwunde'),
    (16.0, 'Reizung'),
    (16.0, 'Verbrennung'),
    (10.0, 'Verätzung'),
    (19.0, 'Prellungen / Schürfwunden'),
]
CHART_DATA = (
    ['2010', '2011', '2012', '2013', '2014'],
    [6, 5, 4, 3, 1],
    [1, 3, 2, 0, 0],
)


def set_items(n, obj, attr, values):
    m = len(values)
    i = m // n
    for j in xrange(n):
        setattr(obj[j], attr, values[j*i % m])


class LegendedPie3d(_DrawingEditorMixin, Drawing):

    def __init__(self, raw_data, width=600, height=300, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        # Pie3d
        self._add(self, Pie3d(), name='pie', validate=None, desc=None)
        self.pie.width = 300
        self.pie.height = self.pie.width
        self.pie.perspective = 40
        self.pie.depth_3d = 15
        self.pie.angle_3d = 180
        self.pie.x = 20
        self.pie.y = (height - self.pie.height) // 2
        _data, _labels = [], []
        for d, l in raw_data:
            _data.append(d)
            _labels.append(l)
        self.pie.data = _data
        self.pie.labels = _labels
        self.pie.simpleLabels = True
        self.pie.slices.label_visible = False
        self.pie.slices.fontColor = None
        self.pie.slices.strokeColor = colors.white
        self.pie.slices.strokeWidth = 0
        self.pie.slices.popout = 10
        self.pie.slices[0].popout = 25
        # Legend
        self._add(self, Legend(), name='legend', validate=None, desc=None)
        self.legend.x = self.pie.width + 80
        self.legend.y = height - 100
        self.legend.dx = 8
        self.legend.dy = 8
        self.legend.columnMaximum = 10
        self.legend.fontSize = 14
        self.legend.alignment = 'right'
        n = len(self.pie.data)
        set_items(n, self.pie.slices, 'fillColor', CHART_COLORS[:n])
        tmp = []
        for i in xrange(n):
            txt = '{0} {1:.1f}%'.format(self.pie.labels[i], self.pie.data[i])
            tmp.append((self.pie.slices[i].fillColor, txt.encode('utf-8')))
        self.legend.colorNamePairs = tmp


class MyBarChart(Drawing):

    def __init__(self, raw_data, width=600, height=300, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self.add(VerticalBarChart3D(), name='bc')
        self.bc.x = 20
        self.bc.y = 20
        self.bc.width = width - 200
        self.bc.height = height - 40
        self.bc.barWidth = 5
        self.bc.data = [tuple(raw_data[1]), tuple(raw_data[2])]
        self.bc.valueAxis.valueMax = max([max(self.bc.data[0]),
                                          max(self.bc.data[1])]) + 1
        self.bc.categoryAxis.categoryNames = raw_data[0]
        self.add(Legend(), name='legend')
        self.legend.x = self.bc.width + 40
        self.legend.y = height // 2
        self.legend.colorNamePairs = [
            (Auto(chart=self.bc), 'Arbeitsunfälle gesamt'.encode('utf-8')),
            (Auto(chart=self.bc), 'davon Wegeunfälle'.encode('utf-8')),
        ]
        self.legend.fontSize = 14
        self.legend.alignment = 'right'


if __name__ == '__main__':
    d = LegendedPie3d(DATA_PIE)
    d.save(formats=['pdf', 'png'])
    bc = MyBarChart(CHART_DATA)
    bc.save(formats=['pdf', 'png'])
