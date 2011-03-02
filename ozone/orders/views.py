# Create your views here.

from datetime import date

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from orders.forms import OrderDayForm
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


def order(req):
    pass


def myorders(req):
    pass
