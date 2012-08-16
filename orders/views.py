# Create your views here.

from datetime import date

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from core.utils import json_view
from core.models import Company
from orders.forms import (OrderDayForm, OrderOldForm, OrderForm,
                          ShortSupplierForm)
from orders.models import OrderDay, Order, Article, Cost, CostOrder
from orders.menu import menus


def get_next_odays(include_today=False):
    if include_today:
        q = dict(day__gte=date.today())
    else:
        q = dict(day__gt=date.today())
    odays = OrderDay.objects.filter(**q).order_by('day')
    return odays


def index(req):
    if req.user.has_perm('orders.can_order'):
        inc = True
    else:
        inc = False
    odays = get_next_odays(inc)
    ctx = dict(page_title=_(u'Orders'), odays=odays, menus=menus)
    return render_to_response('orders/index.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def order_detail(req, order_id):
    oid = int(order_id)
    oday = OrderDay.objects.get(id=oid)
    orders = Order.objects.select_related().filter(order_day=oday
        ).order_by('-added', 'article__name')
    for o in orders:
        o.userlist = [x.username for x in o.users.all()]
    ctx = dict(page_title=_(u'Open Orders'), menus=menus, oday=oday,
        orders=orders)
    ctx.update(csrf(req))
    return render_to_response('orders/orderday.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def order(req, article_id=0):
    if req.method == 'POST':
        form = OrderForm(req.POST)
    else:
        form = OrderForm()
    costs = Cost.objects.all().order_by('ident')
    ctx = dict(page_title=_(u'Orders'), form=form, menus=menus, costs=costs,
        article_id=article_id, costs_msg=_(u'Sum of costs must be 100!'),
        cur_msg=_(u'Price in %s.' % settings.CURRENCY[0]))
    return render_to_response('orders/order.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def ask_order(req):
    if req.method == 'POST':
        form = OrderOldForm(req.POST)
        if form.is_valid():
            return redirect('orders-order', form.cleaned_data['article_id'])
    else:
        form = OrderOldForm()
    articles = [(x.id, x.name, x.short_desc()) for x in
                Article.objects.all().order_by('name')]
    ctx = dict(page_title=_('Orders'), form=form, menus=menus,
        articles=articles)
    return render_to_response('orders/select_article.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def myorders(req):
    orders = req.user.order_set.select_related().all(
        ).order_by('-added', 'article__name')
    ctx = dict(page_title=_('My Orders'), menus=menus, orders=orders)
    return render_to_response('orders/myorders.html', ctx,
                              context_instance=RequestContext(req))


@permission_required('core.add_company')
def add_supplier(req):
    if req.method == 'POST':
        form = ShortSupplierForm(req.POST)
        if form.is_valid():
            c, created = Company.objects.get_or_create(
                name=form.cleaned_data['name'])
            if not created:
                messages.error(req, _(u'Company %s already exists.' % c.name))
                return redirect('orders-index')
            c.customer_number = form.cleaned_data['customer_number']
            c.phone = form.cleaned_data['phone']
            c.fax = form.cleaned_data['fax']
            c.email = form.cleaned_data['email']
            c.save()
            messages.success(req, _(u'New company %s saved.' % c.name))
            return redirect('orders-index')
        messages.error(req, _(u'Please correct the wrong fields.'))
    else:
        form = ShortSupplierForm()
    ctx = dict(page_title=_(u'Add new Supplier'), menus=menus, form=form)
    return render_to_response('orders/new_supplier.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def update_article_count(req, order_id, count):
    print order_id, count
#        id_order = req.POST.get('id_order')
#        count = req.POST.get('count')
#        order = Order.objects.get(id=int(id_order))
#        if count == order.count:
#            messages.error(req, _(u'Count was not changed.'))
#            return redirect('orders-detail', oid)
#        order.count = count
#        if req.user not in order.users:
#            order.users.add(req.user)
#        order.save()
#        messages.success(req, _(u'New count was saved.'))
#        return redirect('orders-detail', oid)


# Ajax
@json_view
def api_article(req, article_id=0):
    article_id = int(article_id)
    if not article_id:
        return {'count': 1}
    oday = get_next_odays()[0]
    a = Article.objects.get(pk=article_id)
    data = dict(art_name=a.name, art_supplier=a.supplier.id,
        art_id=a.ident, art_q=a.quantity, art_price=float(a.price),
        count=1, oday=oday.id)
    return data
