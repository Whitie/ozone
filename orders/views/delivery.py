# -*- coding: utf-8 -*-

from datetime import date, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from orders.models import DeliveredOrder, Order
from orders.menu import menus


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
    last = date.today() - timedelta(days=30)
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
        dorders=dorders)
    return render(req, 'orders/delivery.html', ctx, app=u'orders')
