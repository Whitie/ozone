# Create your views here.

from datetime import date

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from core.utils import json_view
from orders.forms import OrderDayForm, OrderOldForm, OrderForm
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


def order_detail(req, order_id):
    pass


@login_required
def order(req, article_id=0):
    if req.method == 'POST':
        form = OrderForm(req.POST)
    else:
        form = OrderForm()
    oday = get_next_odays()[0]
    costs = Cost.objects.all()
    ctx = dict(page_title=_(u'Orders'), form=form, menus=menus, costs=costs,
        article_id=article_id)
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
    order_list = req.user.order_set.all().order_by('-added', 'article__name')
    paginator = Paginator(order_list, 20)
    try:
        page = int(req.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        orders = paginator.page(page)
    except (EmptyPage, InvalidPage):
        orders = paginator.page(paginator.num_pages)
    ctx = dict(page_title=_('My Orders'), menus=menus, orders=orders)
    return render_to_response('orders/myorders.html', ctx,
                              context_instance=RequestContext(req))

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
