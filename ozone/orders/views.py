# Create your views here.

from datetime import date

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from orders.forms import OrderDayForm, OrderOldForm, OrderForm
from orders.models import OrderDay, Order
from orders.menu import menus


def index(req):
    if req.user.has_perm('orders.can_order'):
        q = dict(day__gte=date.today())
    else:
        q = dict(day__gt=date.today())
    odays = OrderDay.objects.select_related().filter(**q).order_by('day')
    ctx = dict(page_title=_(u'Orders'), odays=odays, menus=menus)
    return render_to_response('orders/index.html', ctx,
                              context_instance=RequestContext(req))


def order_detail(req, order_id):
    pass


@login_required
def order(req, article=None):
    pass


@login_required
def ask_order(req):
    if req.method == 'POST':
        form = OrderOldForm(req.POST)
        if form.is_valid():
            return redirect('orders-order', form.cleaned_data['article'])
    else:
        form = OrderOldForm()
    ctx = dict(page_title=_('Orders'), form=form, menus=menus)
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
