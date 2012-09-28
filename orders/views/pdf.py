# -*- coding: utf-8 -*-

import codecs
import os

from datetime import date

from django.core.files.base import ContentFile
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy as _

from core import latex
from core.utils import json_rpc
from core.models import Company, PDFPrintout
from orders.models import Order, OrderDay, Printout, Cost, CostOrder
from orders.menu import menus


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.normpath(
    os.path.join(PATH, '..', 'templates', 'latex'))


def get_orders(oday, supplier=None):
    all_orders = Order.objects.select_related(
        ).filter(order_day=oday, state__in=[u'accepted', u'ordered'])
    if supplier is not None:
        return all_orders.filter(article__supplier=supplier)
    companies = set()
    for o in all_orders:
        companies.add(o.article.supplier)
    orders = []
    for c in companies:
        orders.append(all_orders.filter(article__supplier=c))
    return orders


def summarize_orders(orders):
    summarized = []
    art_ids = set([x.article.id for x in orders])
    for i in art_ids:
        art_count = orders.filter(article__id=i).count()
        if art_count == 1:
            summarized.append(orders.get(article__id=i))
        else:
            order = orders.filter(article__id=i)[0]
            for o in orders.filter(article__id=i)[1:]:
                order.count += o.count
            summarized.append(order)
    return summarized


def clean_file(filename):
    try:
        os.remove(filename)
    except:
        pass


def make_latex(ctx, template, includefile=None):
    if 'supplier' not in ctx:
        ctx['supplier'] = u'ALL'
    env = latex.get_latex_env(TEMPLATE_PATH)
    s = latex.get_latex_settings()
    if includefile is not None:
        ttpl = env.get_template(includefile)
        tfilename = os.path.join(s['build_dir'],
            '{0}_{1}'.format(ctx['supplier'].id, includefile))
        clean_file(tfilename)
        with codecs.open(tfilename, 'w', encoding='utf-8') as fp:
            fp.write(ttpl.render(**ctx))
        ctx['includefile'] = unicode(tfilename).replace(u'\\', u'/')
    tpl = env.get_template(template)
    _id = getattr(ctx['supplier'], 'id', 'ALL')
    filename = os.path.join(s['build_dir'], '{0}_{1}_{2}'.format(_id,
        ctx['oday'].id, template))
    clean_file(filename)
    with codecs.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(tpl.render(**ctx))
    pdfname, r1, r2 = latex.render_latex_to_pdf(filename)
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
    ctx['orders'] = summarize_orders(orders)
    return make_latex(ctx, 'order_fax.tex')


def generate_internal(_ctx):
    ctx = _ctx.copy()
    orders = get_orders(ctx['oday'])
    ctx['costs'] = Cost.objects.all()
    sums = {}
    allsum = 0
    for supp in orders:
        sup_id = supp[0].article.supplier.id
        sums[sup_id] = 0
        for o in supp:
            # Only set state and date on first generation
            if o.state == u'accepted':
                o.state = u'ordered'
                o.ordered = date.today()
                o.save()
            o.userlist = [x.username for x in o.users.all()]
            sums[sup_id] += o.count * o.article.price
            allsum += o.count * o.article.price
            o._costs = []
            costs = list(o.costs.all())
            for c in Cost.objects.all():
                if c in costs:
                    cost = CostOrder.objects.get(order=o, cost=c)
                    o._costs.append(u'{0}'.format(cost.percent))
                else:
                    o._costs.append(u'')
    ctx['sums'] = sums
    ctx['allsum'] = allsum
    ctx['orders'] = orders
    ctx['tbl'] = u'c' * Cost.objects.all().count()
    return make_latex(ctx, 'order.tex')


@require_POST
@permission_required('orders.can_order')
def generate_pdf(req):
    oday_id = int(req.POST.get('oday_id'))
    header = req.POST.get('header', u'')
    oday = OrderDay.objects.get(id=oday_id)
    orders = get_orders(oday)
    supplier = []
    for s in [x[0].article.supplier for x in orders]:
        s.ocount = Order.objects.filter(article__supplier=s, order_day=oday,
            state__in=[u'accepted', u'ordered']).count()
        supplier.append(s)
    supplier_ids = [x[0].article.supplier.id for x in orders]
    req.session['extra_orders'] = []
    req.session['oday_id'] = None
    ctx = dict(page_title=_(u'Printouts'), menus=menus, oday=oday,
        ids=supplier_ids, supplier=supplier, header=header)
    return render(req, 'orders/printouts.html', ctx)


@require_POST
@json_rpc
def generate_one_pdf(req, data):
    oday_id = data.get('oday_id')
    supplier_id = data.get('supplier_id', None)
    header = data.get('header', u'')
    oday = OrderDay.objects.get(id=oday_id)
    s = latex.get_latex_settings()
    ctx = dict(s=s, oday=oday, user=req.user, header=header)
    if supplier_id is not None:
        supplier = Company.objects.get(id=supplier_id)
        printout, filename = generate_external(supplier, ctx)
        return dict(size=printout.pdf.size, filename=filename,
            url=printout.pdf.url)
    else:
        printout, filename = generate_internal(ctx)
        return dict(size=printout.pdf.size, filename=filename,
            url=printout.pdf.url)


@require_POST
@json_rpc
def generate_ratings_pdf(req, data=None):
    return {'msg': u'Test'}
