# -*- coding: utf-8 -*-

import codecs
import os

from datetime import date

from django.core.files.base import ContentFile
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy as _

from core import latex
from core.utils import json_rpc
from core.models import Company
from orders.models import Order, OrderDay, Printout, Cost, CostOrder
from orders.menu import menus


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(PATH, 'latex')
BUILD_PATH = os.path.join(TEMPLATE_PATH, '_build')


def get_orders(oday, supplier=None):
    all_orders = Order.objects.select_related(
        ).filter(order_day=oday, state=u'accepted')
    if supplier is not None:
        return all_orders.filter(article__supplier=supplier)
    companies = set()
    for o in all_orders:
        companies.add(o.article.supplier)
    orders = []
    for c in companies:
        orders.append(all_orders.filter(article__supplier=c))
    return orders


def make_latex(ctx, template, includefile=None):
    if 'supplier' not in ctx:
        ctx['supplier'] = u'ALL'
    env = latex.get_latex_env(TEMPLATE_PATH)
    if includefile is not None:
        ttpl = env.get_template(includefile)
        tfilename = os.path.join(BUILD_PATH,
            '{0}_{1}'.format(ctx['supplier'].id, includefile))
        with codecs.open(tfilename, 'w', encoding='utf-8') as fp:
            fp.write(ttpl.render(**ctx))
        ctx['includefile'] = unicode(tfilename).replace(u'\\', u'/')
    tpl = env.get_template(template)
    _id = getattr(ctx['supplier'], 'id', 'ALL')
    filename = os.path.join(BUILD_PATH, '{0}_{1}'.format(_id, template))
    with codecs.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(tpl.render(**ctx))
    pdfname, r1, r2 = latex.render_latex_to_pdf(filename, BUILD_PATH)
    pdf = os.path.split(pdfname)[1]
    _name = getattr(ctx['supplier'], 'name', u'ALL')
    printout, created = Printout.objects.get_or_create(order_day=ctx['oday'],
        internal=_name == u'ALL', company_name=_name)
    with open(pdfname, 'rb') as fp:
        content = ContentFile(fp.read())
    printout.pdf.save(pdf, content)
    printout.save()
    return printout, pdf


def generate_external(supplier, _ctx):
    ctx = _ctx.copy()
    orders = get_orders(ctx['oday'], supplier)
    ctx['supplier'] = supplier
    ctx['orders'] = orders
    return make_latex(ctx, 'order_fax.tex')


def generate_internal(_ctx):
    ctx = _ctx.copy()
    orders = get_orders(ctx['oday'])
    ctx['costs'] = Cost.objects.all()
    sums = {}
    for supp in orders:
        sup_id = supp[0].article.supplier.id
        sums[sup_id] = 0
        for o in supp:
            o.state = u'ordered'
            o.ordered = date.today()
            o.save()
            sums[sup_id] += o.count * o.article.price
            o._costs = []
            costs = list(o.costs.all())
            for c in Cost.objects.all():
                if c in costs:
                    cost = CostOrder.objects.get(order=o, cost=c)
                    o._costs.append(u'{0}'.format(cost.percent))
                else:
                    o._costs.append(u'')
    ctx['sums'] = sums
    ctx['orders'] = orders
    ctx['tbl'] = u'c' * Cost.objects.all().count()
    return make_latex(ctx, 'order.tex')


@require_POST
@permission_required('orders.can_order')
def generate_pdf(req):
    for f in os.listdir(BUILD_PATH):
        try:
            os.remove(os.path.join(BUILD_PATH, f))
        except:
            pass
    oday_id = int(req.POST.get('oday_id'))
    oday = OrderDay.objects.get(id=oday_id)
    orders = get_orders(oday)
    supplier_ids = [x[0].article.supplier.id for x in orders]
    ctx = dict(page_title=_(u'Printouts'), menus=menus, oday=oday,
        ids=supplier_ids)
    return render_to_response('orders/printouts.html', ctx,
                              context_instance=RequestContext(req))


@require_POST
@json_rpc
def generate_one_pdf(req, data):
    oday_id = data.get('oday_id')
    supplier_id = data.get('supplier_id', None)
    oday = OrderDay.objects.get(id=oday_id)
    s = latex.get_latex_settings()
    ctx = dict(s=s, oday=oday, user=req.user)
    if supplier_id is not None:
        supplier = Company.objects.get(id=supplier_id)
        printout, filename = generate_external(supplier, ctx)
        return dict(supplier=supplier.short_name or supplier.name,
            size=printout.pdf.size, filename=filename,
            url=printout.pdf.url)
    else:
        printout, filename = generate_internal(ctx)
        return dict(size=printout.pdf.size, filename=filename,
            url=printout.pdf.url)
