# Create your views here.

from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core.utils import json_view, json_rpc, any_permission_required
from core.models import Company
from orders.forms import (OrderOldForm, OrderForm, ShortSupplierForm,
                          OrderDayForm)
from orders.models import OrderDay, Order, Article, Cost, CostOrder
from orders.menu import menus


# Helper

def get_user_choices():
    return [(x.id, x.get_full_name() or x.username) for x in
            User.objects.all() if x.has_perm('orders.can_order')]


def get_supplier_choices():
    l = []
    for c in Company.objects.all().order_by('name'):
        if not c.has_students():
            if len(c.name) > 22:
                name = u'{0}...'.format(c.name[:22])
            else:
                name = c.name
            l.append((c.id, name))
    return l


def get_oday_choices(filters):
    return [(x.id, unicode(x)) for x in
            OrderDay.objects.filter(**filters).order_by('day')]


def get_price(value):
    value = value.replace(u',', u'.')
    return Decimal(value)


def get_next_odays(include_today=False):
    if include_today:
        q = dict(day__gte=date.today() - timedelta(days=1))
    else:
        q = dict(day__gt=date.today())
    odays = OrderDay.objects.filter(**q).order_by('day')
    return odays


def get_costs(data):
    costs = []
    for k, v in data.items():
        if k.startswith('cost_') and int(v):
            ident = int(k[5:])
            percent = int(v)
            cost = Cost.objects.get(ident=ident)
            costs.append((cost, percent))
    return costs


# Views

def index(req):
    if req.user.has_perm('orders.can_order'):
        inc = True
    else:
        inc = False
    odays = get_next_odays(inc)
    ctx = dict(page_title=_(u'Orders'), odays=odays, menus=menus)
    return render(req, 'orders/index.html', ctx)


@login_required
def order_detail(req, order_id):
    oid = int(order_id)
    oday = OrderDay.objects.get(id=oid)
    orders = Order.objects.select_related().filter(order_day=oday
        ).order_by('-added', 'article__name')
    order_sum = 0
    for o in orders:
        o.userlist = [x.username for x in o.users.all()]
        o.costlist = [u'%s: %d%%' % (unicode(x.cost), x.percent) for x in
                      CostOrder.objects.filter(order=o)]
        order_sum += o.count * o.article.price
        o.sum_price = o.count * o.article.price
        if req.user.username in o.userlist and o.users.count() == 1 and\
            o.state in (u'new', u'accepted', u'rejected'):
            o.deleteable = True
        else:
            o.deleteable = False
    ctx = dict(page_title=_(u'Open Orders'), menus=menus, oday=oday,
        orders=orders, not_changed=_(u'Count was not changed. Aborting.'),
        order_sum=order_sum)
    req.session['came_from'] = 'orders-detail'
    req.session['came_from_kw'] = {'order_id': order_id}
    return render(req, 'orders/orderday.html', ctx)


@login_required
def delete_order(req, oday_id, order_id):
    order = Order.objects.get(id=int(order_id))
    if req.method == 'POST':
        answer = req.POST.get('delete', u'no')
        redirect_to = req.session.get('came_from', 'orders-detail')
        kw = req.session.get('came_from_kw', {'order_id': oday_id})
        if req.user.id not in [x.id for x in order.users.all()] or \
                order.users.count() > 1:
            if not req.user.has_perm('orders.can_order'):
                messages.error(req, _(u'Cannot delete foreign order!'))
                return redirect(redirect_to, **kw)
        if answer == u'yes':
            order.delete()
            messages.success(req, _(u'Order (ID: %s) deleted.' % order_id))
        else:
            messages.error(req, _(u'Nothing deleted. Cancelled by user.'))
        return redirect(redirect_to, **kw)
    ctx = dict(page_title=_(u'Delete Order'), menus=menus, oday_id=oday_id,
        order=order)
    return render(req, 'orders/delete.html', ctx)


@login_required
def order(req, article_id=0):
    if req.user.has_perm('orders.can_order'):
        choice_filter = {'day__gte': date.today() - timedelta(days=1)}
    else:
        choice_filter = {'day__gt': date.today()}
    if req.method == 'POST':
        form = OrderForm(req.POST)
        form.fields['art_supplier'].choices = get_supplier_choices()
        form.fields['oday'].choices = get_oday_choices(choice_filter)
        if form.is_valid():
            costs = get_costs(req.POST)
            art, created = Article.objects.get_or_create(
                name=form.cleaned_data['art_name'],
                ident=form.cleaned_data['art_id'],
                price=get_price(form.cleaned_data['art_price']))
            if created:
                art.quantity = form.cleaned_data['art_q']
                art.supplier = Company.objects.get(
                    id=int(form.cleaned_data['art_supplier']))
                art.save()
            order = Order.objects.create(count=form.cleaned_data['count'],
                article=art,
                order_day=OrderDay.objects.get(
                    id=int(form.cleaned_data['oday'])))
            order.save()
            for cost, percent in costs:
                co = CostOrder.objects.create(percent=percent, order=order,
                    cost=cost)
                co.save()
            order.memo = form.cleaned_data['memo']
            order.for_test = form.cleaned_data['exam']
            order.for_repair = form.cleaned_data['repair']
            order.users.add(req.user)
            order.save()
            messages.success(req, _(u'Your order %s was saved.' % order))
            return redirect('orders-detail', order_id=order.order_day.id)
        messages.error(req, _(u'Please fill the required fields.'))
    else:
        form = OrderForm()
        form.fields['art_supplier'].choices = get_supplier_choices()
        form.fields['oday'].choices = get_oday_choices(choice_filter)
    costs = Cost.objects.all().order_by('ident')
    ctx = dict(page_title=_(u'Orders'), form=form, menus=menus, costs=costs,
        article_id=article_id, costs_msg=_(u'Sum of costs must be 100!'),
        cur_msg=_(u'Price in %s.' % settings.CURRENCY[0]))
    return render(req, 'orders/order.html', ctx)


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
    ctx = dict(page_title=_(u'Orders'), form=form, menus=menus,
        articles=articles)
    return render(req, 'orders/select_article.html', ctx)


@login_required
def myorders(req):
    order_list = req.user.order_set.select_related().all(
        ).order_by('article__name', '-added')
    orders = []
    ids = set()
    for o in order_list:
        if not o.article.id in ids:
            ids.add(o.article.id)
            orders.append(o)
    ctx = dict(page_title=_(u'My Orders'), menus=menus, orders=orders)
    return render(req, 'orders/myorders.html', ctx)


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
            c.short_name = form.cleaned_data['name'].upper()
            c.customer_number = form.cleaned_data['customer_number']
            c.phone = form.cleaned_data['phone']
            c.fax = form.cleaned_data['fax']
            c.email = form.cleaned_data['email']
            c.rating_users.add(req.user)
            c.save()
            messages.success(req, _(u'New company %s saved.' % c.name))
            return redirect('orders-index')
        messages.error(req, _(u'Please correct the wrong fields.'))
    else:
        form = ShortSupplierForm()
    ctx = dict(page_title=_(u'Add new Supplier'), menus=menus, form=form)
    return render(req, 'orders/new_supplier.html', ctx)


@any_permission_required(['orders.can_order', 'orders.can_change_orderstate'],
                         raise_exception=True)
def manage_orders(req):
    if req.method == 'POST':
        day = int(req.POST['oday'])
        oday = OrderDay.objects.select_related().get(id=day)
        messages.success(req, _(u'%s selected.' % oday))
        return redirect('orders-manage', oday_id=day)
    users = User.objects.exclude(username='admin')
    can_order = [x.username for x in users if x.has_perm('orders.can_order')]
    can_change = [x.username for x in users
                  if x.has_perm('orders.can_change_orderstate')]
    limit = date.today() - timedelta(days=14)
    odays = OrderDay.objects.filter(day__gte=limit).order_by('day')
    ctx = dict(page_title=_(u'Manage Orders'), menus=menus, odays=odays,
        users=users, can_order=can_order, can_change=can_change)
    return render(req, 'orders/manage_orders.html', ctx)


@any_permission_required(['orders.can_order', 'orders.can_change_orderstate'],
                         raise_exception=True)
def manage_order(req, oday_id):
    oday = OrderDay.objects.get(id=int(oday_id))
    orders = Order.objects.select_related().filter(order_day=oday)
    order_sum = 0
    for o in orders:
        o.userlist = [x.username for x in o.users.all()]
        order_sum += o.count * o.article.price
        o.sum_price = o.count * o.article.price
    ctx = dict(page_title=_(u'Manage Orders'), menus=menus, oday=oday,
        orders=orders, states=(u'new', u'accepted', u'rejected'),
        order_sum=order_sum)
    req.session['came_from'] = 'orders-manage'
    req.session['came_from_kw'] = {'oday_id': oday_id}
    return render(req, 'orders/manage_order.html', ctx)


@permission_required('orders.can_order', raise_exception=True)
def add_oday(req):
    if req.method == 'POST':
        form = OrderDayForm(req.POST)
        form.fields['user'].choices = get_user_choices()
        if form.is_valid():
            if form.cleaned_data['user'].is_anonymous():
                messages.error(req, _(u'The user you specified is not valid.'))
                return redirect('orders-manage')
            oday = OrderDay.objects.create(day=form.cleaned_data['day'],
                user=form.cleaned_data['user'])
            oday.save()
            messages.success(req, _(u'New orderday %s added.' % unicode(oday)))
            return redirect('orders-manage')
        else:
            messages.error(req, _(u'Please correct the form.'))
    else:
        form = OrderDayForm()
        form.fields['user'].choices = get_user_choices()
    odays = get_next_odays(True)
    ctx = dict(page_title=_(u'Add new orderday'), menus=menus, form=form,
        odays=[unicode(x) for x in odays])
    return render(req, 'orders/add_oday.html', ctx)


@permission_required('orders.can_order', raise_exception=True)
def list_printouts(req):
    odays = OrderDay.objects.select_related().all().order_by('-day')
    for oday in odays:
        oday.price = 0
        oday.count = 0
        for o in oday.orders.all():
            oday.price += o.price()
            oday.count += 1
    ctx = dict(page_title=_(u'List of all printouts'), menus=menus,
        odays=odays)
    return render(req, 'orders/list_printouts.html', ctx)


# Ajax views

@json_view
def update_article_count(req, order_id, count):
    order_id, count = int(order_id), int(count)
    order = Order.objects.select_related().get(id=order_id)
    old_count = order.count
    order.count = count
    try:
        u = order.users.get(id=req.user.id)
    except:
        order.users.add(req.user)
    order.save()
    msg = _(u'Count for %(name)s was changed from %(old)d to %(count)d.' %
        {'name': order.article.name, 'old': old_count, 'count': count})
    user = [x.username for x in order.users.all()]
    return dict(msg=unicode(msg), user=u', '.join(user))


@json_view
def get_articles(req):
    articles = [{'value': x.id, 'label': x.name, 'desc': x.short_desc()}
                for x in Article.objects.all().order_by('name')]
    return articles


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


@require_POST
@json_view
def add_representative(req):
    users = map(int, req.POST.getlist('users[]', []))
    action_type = req.POST.get('type')
    perm = Permission.objects.get(codename=action_type)
    added = []
    removed = []
    msgs = []
    for u in User.objects.exclude(username='admin'):
        if u.id in users:
            if not u.has_perm('orders.%s' % action_type):
                added.append(u.username)
                u.user_permissions.add(perm)
        else:
            if u.has_perm('orders.%s' % action_type):
                removed.append(u.username)
                u.user_permissions.remove(perm)
    if added:
        msgs.append(_(u'%s added.' % u', '.join(added)))
    if removed:
        msgs.append(_(u'%s removed.' % u', '.join(removed)))
    return {'msg': u' '.join([unicode(x) for x in msgs])}


@require_POST
@json_rpc
def change_order(req, data):
    print data
    try:
        order_id = int(data['order_id'])
        count = int(data['count'])
        state = data['state']
        art_name = data['art_name']
        art_ident = data['art_ident']
        price = Decimal(data['price'].replace(u',', u'.'))
        order = Order.objects.get(id=order_id)
        article = order.article
        article.name = art_name
        article.ident = art_ident
        article.price = price
        article.save()
        order.count = count
        order.state = state
        order.save()
        msg = _(u'All changes to order with ID %d saved.' % order_id)
    except Exception as e:
        msg = e
    return {'msg': unicode(msg)}
