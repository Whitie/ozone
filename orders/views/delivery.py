# -*- coding: utf-8 -*-

from datetime import date, timedelta

from django.contrib.auth.decorators import login_required, permission_required
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
