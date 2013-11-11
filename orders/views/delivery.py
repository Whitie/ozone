# -*- coding: utf-8 -*-

import csv

from cStringIO import StringIO

from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from orders.models import DeliveredOrder, Order, Article
from orders.views import helper as h
from orders.menu import menus
from core.utils import render


@login_required
def index(req):
    orders = []
    for o in Order.objects.select_related().filter(state=u'ordered'
        ).order_by('-ordered', 'article__name'):
        o.dsum = 0
        for d in DeliveredOrder.objects.filter(order=o):
            o.dsum += d.count
        o.missing = o.count - o.dsum
        o.userlist = [x.username for x in o.users.all()]
        orders.append(o)
    tmp = set()
    last = date.today() - timedelta(days=14)
    for d in DeliveredOrder.objects.select_related().filter(
        order__state=u'delivered', date__gte=last):
        if d.order.is_complete():
            tmp.add(d.order.id)
    dorders = []
    for o in Order.objects.select_related().filter(id__in=list(tmp)
        ).order_by('-ordered', 'article__name'):
        avg_days = 0
        counter = 0
        for d in DeliveredOrder.objects.filter(order=o):
            dt = d.date - o.ordered
            avg_days += dt.days
            counter += 1
        o.avg_days = avg_days / float(counter)
        o.userlist = [x.username for x in o.users.all()]
        dorders.append(o)
    ctx = dict(page_title=_(u'Delivery'), menus=menus, orders=orders,
        dorders=dorders, dt=True, need_ajax=True)
    return render(req, 'orders/delivery/index.html', ctx, app=u'orders')


@permission_required('orders.can_order')
def delivery_by_barcode(req):
    # All functionality is provided by ajax functions.
    ctx = dict(page_title=_(u'Delivery'), subtitle=_('By barcode'),
        need_ajax=True, menus=menus)
    return render(req, 'orders/delivery/barcodes.html', ctx, app=u'orders')


@permission_required('orders.can_order')
def get_article_by_barcode(req, barcode):
    bc = barcode.strip()
    bc = h.extract_barcode(bc)
    try:
        article = Article.objects.select_related().get(barcode=bc)
    except Article.DoesNotExist:
        article = None
    if article is not None:
        orders = Order.objects.select_related().filter(state=u'ordered',
            article=article).order_by('ordered')
        if orders:
            for o in orders:
                o.delivered = 0
                for d in DeliveredOrder.objects.filter(order=o):
                    o.delivered += d.count
            ctx = dict(orders=orders, article=article, olen=len(orders))
            return render(req, 'orders/delivery/known_bc.html', ctx)
        else:
            ctx = dict(article=article)
            return render(req, 'orders/delivery/error.html', ctx)
    else:
        articles = Article.objects.filter(order__state=u'ordered',
            barcode=u'').order_by('name')
        ctx = dict(articles=articles, barcode=bc)
        return render(req, 'orders/delivery/new_bc.html', ctx)


def _export(ids):
    now = datetime.now()
    choice = DeliveredOrder.objects.select_related().filter(
        id__in=ids).order_by('date')
    if choice.count():
        name = now.strftime('Toxolution_Export_%Y-%m-%d_%H%M%S.csv')
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            name)
        writer = csv.writer(resp, dialect=csv.excel, delimiter=';')
        for c in choice:
            o = c.order
            a = c.order.article
            value, unit = h.split_unit(a.quantity)
            tmp = [c.date.strftime('%Y-%m-%d'), a.name, a.ident,
                a.supplier.name, o.count, u'{:.2f}'.format(value), unit,
                float(a.price), a.barcode]
            row = []
            for x in tmp:
                if isinstance(x, unicode):
                    row.append(x.encode('latin1', errors='replace'))
                else:
                    row.append(x)
            writer.writerow(row)
            c.exported = True
            c.save()
        return resp
    return redirect('orders-csv-export')


@permission_required('orders.can_order')
def export_to_csv(req):
    if req.method == 'POST':
        ids = map(int, req.POST.getlist('export'))
        return _export(ids)
    to_export = DeliveredOrder.objects.select_related().filter(
        exported=False, order__article__tox_control=True).order_by('date')
    ctx = dict(page_title=u'Toxolution Export', menus=menus,
        to_export=to_export, subtitle=u'Gelieferte Bestellungen')
    return render(req, 'orders/delivery/csv_export.html', ctx, app=u'orders')

