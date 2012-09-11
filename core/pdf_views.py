# -*- coding: utf-8 -*-

import codecs
import os

from calendar import monthrange
from datetime import date, timedelta

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from core import utils
from core import latex
from core.models import Student, StudentGroup

try:
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(PATH, 'latex')
BUILD_PATH = os.path.join(TEMPLATE_PATH, '_build')


def iter_days(start, end):
    delta = end - start
    for i in xrange(delta.days):
        yield start + timedelta(days=i)


def make_latex(ctx, template):
    env = latex.get_latex_env(TEMPLATE_PATH)
    tpl = env.get_template(template)
    name = unicode(ctx['group'])
    filename = os.path.join(BUILD_PATH, '{0}_{1}'.format(name, template))
    with codecs.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(tpl.render(**ctx))
    pdfname, r1, r2 = latex.render_latex_to_pdf(filename, BUILD_PATH)
    return pdfname


@utils.check_for_import(canvas, _('PDF generation is not installed.'))
@login_required
def pdf(req, what='grouplist'):
    response = HttpResponse(mimetype='application/pdf')
    p = canvas.Canvas(response)
    p.drawString(100, 100, u'Hello World!')
    p.showPage()
    p.save()
    return response


@login_required
def generate_presence_clean(req, gid, year, month):
    year = int(year)
    month = int(month)
    s = latex.get_latex_settings()
    group = StudentGroup.objects.get(id=int(gid))
    students = Student.objects.filter(group=group
        ).order_by('company__short_name', 'lastname')
    ctx = dict(s=s, group=group, students=students)
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    ctx['day_nums'] = [x.day for x in iter_days(start, end)
                       if x.weekday() not in (5, 6)]
    ctx['edu_year'] = utils.get_edu_year(group.start_date)
    ctx['timespan'] = unicode(start.strftime('%B %Y'))
    ctx['schooldays'] = []
    ctx['instructor'] = unicode(req.user.get_profile())
    ctx['course'] = u''
    ctx['table_days'] = [u'c' for x in ctx['day_nums']]
    filename = make_latex(ctx, 'awhl_leer.tex')
    with open(filename, 'rb') as fp:
        response = HttpResponse(fp.read(), content_type='application/pdf')
    return response
