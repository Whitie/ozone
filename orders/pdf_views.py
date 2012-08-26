# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy as _

from core.utils import json_view
from orders.models import Order, OrderDay
from orders.menu import menus


@require_POST
@permission_required('orders.can_order')
def generate_pdf(req):
    oday_id = int(req.POST.get('oday_id'))
    oday = OrderDay.objects.get(id=oday_id)
    ctx = dict(page_title=_(u'Printouts'), menus=menus, oday=oday)
    return render_to_response('orders/printouts.html', ctx,
                              context_instance=RequestContext(req))


@require_POST
@json_view
def generate_one_pdf(req):
    oday_id = int(req.POST.get('oday_id'))
    oday = OrderDay.objects.get(id=oday_id)
    all_orders = Order.objects.select_related(
        ).filter(order_day=oday, state=u'accepted')
    companies = set()
    for o in all_orders:
        companies.add(o.article.supplier)
    print companies
    orders = []
    for c in companies:
        orders.append(all_orders.filter(article__supplier=c))
    print orders
    return {}
