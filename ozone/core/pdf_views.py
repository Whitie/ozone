# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required, permission_required

from core import utils

try:
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None


def check_pdfgen(f):
    def error(req, *args, **kwargs):
        return utils.error(req, _('PDF generation is not installed.'))
    if canvas is None:
        return error
    else:
        return f


@check_pdfgen
@login_required
def pdf(req, what='grouplist'):
    response = HttpResponse(mimetype='application/pdf')
    p = canvas.Canvas(response)
    p.drawString(100, 100, u'Hello World!')
    p.showPage()
    p.save()
    return response
