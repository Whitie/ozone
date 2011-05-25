# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from reportlab.pdfgen import canvas


@login_required
def pdf(req, what='grouplist'):
    response = HttpResponse(mimetype='application/pdf')
    p = canvas.Canvas(response)
    p.drawString(100, 100, u'Hello World!')
    p.showPage()
    p.save()
    return response
