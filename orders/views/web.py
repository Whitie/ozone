# -*- coding: utf-8 -*-
# Create your views here.

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from core.utils import any_permission_required, render
from core.models import Company, CompanyRating, PDFPrintout
from core.forms import CompanyRatingForm
from orders.forms import (OrderForm, ShortSupplierForm,
                          OrderDayForm, BaseOrderForm, SummarizeForm)
from orders.models import OrderDay, Order, Article, Cost, CostOrder, _mapper
from orders.views import helper as h
from orders.menu import menus


# Views

def index(req):
    inc = req.user.has_perm('orders.can_order')
    odays = list(h.get_next_odays(inc))
    ctx = dict(page_title=_(u'Next order days'), odays=odays, menus=menus)
    if odays:
        diff = odays[0].day - date.today()
        ctx['subtitle'] = _(u'Next in {0} days'.format(diff.days))
    oday_count = len(odays)
    if oday_count < 2 and inc:
        if oday_count == 1:
            messages.warning(req, u'Es ist nur noch 1 Bestelltag angelegt!')
        else:
            messages.error(req, u'Es ist kein Bestelltag mehr angelegt!')
    return render(req, 'orders/index.html', ctx, app=u'orders')


@login_required
def show_old_orders(req):
    orders = h.get_order_for_every_article()
    try:
        first = Order.objects.all().order_by('added')[0]
        dt = first.added.strftime(settings.DEFAULT_DATE_FORMAT)
    except:
        dt = u''
    ctx = dict(page_title=_(u'All ordered articles'), menus=menus,
        orders=orders, dt=True, subtitle=_(u'Since {0}'.format(dt)))
    return render(req, 'orders/old_orders.html', ctx, app=u'orders')


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
        orders=orders, order_sum=order_sum, subtitle=unicode(oday), dt=True,
        need_ajax=True)
    return render(req, 'orders/orderday.html', ctx, app=u'orders')


@login_required
def order(req, article_id=0):
    if req.user.has_perm('orders.can_order'):
        choice_filter = {'day__gte': date.today() - timedelta(days=1)}
    else:
        choice_filter = {'day__gt': date.today()}
    if req.method == 'POST':
        form = OrderForm(req.POST)
        form.fields['oday'].choices = h.get_oday_choices(choice_filter)
        if form.is_valid():
            company = Company.objects.get(
                id=form.cleaned_data['art_supplier_id'])
            costs = h.get_costs(req.POST)
            art, created = Article.objects.get_or_create(
                name=form.cleaned_data['art_name'],
                ident=form.cleaned_data['art_id'],
                price=h.get_price(form.cleaned_data['art_price']))
            if created:
                art.quantity = form.cleaned_data['art_q']
                art.supplier = company
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
            # Add orderer to rating_users
            if req.user.id not in [x.id for x in company.rating_users.all()]:
                company.rating_users.add(req.user)
                company.save()
                messages.success(req, u'Sie wurden als Bewerter für %s '
                                      u'hinzugefügt.' % company.name)
            messages.success(req, u'Ihre Bestellung %s wurde gespeichert.'
                             % order)
            return redirect('orders-detail', order_id=order.order_day.id)
        messages.error(req, u'Bitte füllen Sie die benötigten Felder aus.')
    else:
        form = OrderForm()
        form.fields['oday'].choices = h.get_oday_choices(choice_filter)
    costs = Cost.objects.all().order_by('ident')
    ctx = dict(page_title=_(u'New Order'), form=form, menus=menus, costs=costs,
        article_id=article_id, costs_msg=_(u'Sum of costs must be 100!'),
        cur_msg=_(u'Price in %s.' % settings.CURRENCY[0]), extra=False,
        need_ajax=True)
    return render(req, 'orders/order.html', ctx, app=u'orders')


@login_required
def ask_order(req):
    if req.method == 'POST':
        article_id = req.POST.get('article_id')
        if article_id:
            return redirect('orders-order', article_id)
        else:
            messages.error(req, u'Kein Artikel ausgewählt.')
    ctx = dict(page_title=_(u'Make order'), menus=menus)
    return render(req, 'orders/select_article.html', ctx, app=u'orders')


@login_required
def myorders(req):
    _orders = req.user.order_set.select_related().all()
    orders = []
    for s in u'delivered', u'new', u'accepted', u'ordered', u'rejected':
        state = dict(name=s, btn=_mapper[s][0], icon=_mapper[s][1])
        tmp = []
        ids = set()
        for o in _orders.filter(state=s).order_by('article__name', '-added'):
            if not o.article.id in ids:
                ids.add(o.article.id)
                tmp.append(o)
        orders.append((state, tmp))
    ctx = dict(page_title=_(u'My Orders'), dt=True, need_ajax=True,
        subtitle=unicode(req.user.get_profile()),
        menus=menus, orders=orders)
    return render(req, 'orders/myorders.html', ctx, app=u'orders')


@permission_required('core.add_company')
def add_supplier(req):
    if req.method == 'POST':
        form = ShortSupplierForm(req.POST)
        if form.is_valid():
            cd = form.cleaned_data
            c, created = Company.objects.get_or_create(name=cd['name'])
            if not created:
                messages.error(req, u'Lieferant %s existiert bereits.' %
                               c.name)
                return redirect('orders-index')
            c.customer_number = cd['customer_number']
            c.phone = cd['phone']
            c.fax = cd['fax']
            c.email = cd['email']
            c.web = cd['web']
            c.rating_users.add(req.user)
            c.save()
            messages.success(req, u'Neuer Lieferant %s gespeichert.' % c.name)
            messages.success(req, u'Sie wurden als Bewerter für diesen '
                                  u'Lieferanten eingetragen.')
            return redirect('orders-index')
        messages.error(req, u'Bitte korrigieren Sie die falschen Felder.')
    else:
        form = ShortSupplierForm(initial={'web': 'http://'})
    ctx = dict(page_title=_(u'Add new Supplier'), menus=menus, form=form,
        need_ajax=True)
    return render(req, 'orders/new_supplier.html', ctx, app=u'orders')


@any_permission_required(['orders.can_order', 'orders.extra_order'],
                         raise_exception=True)
def make_extra_order(req, article_id=0):
    _orders = req.session.get('extra_orders', [])
    oday_id = req.session.get('oday_id', None)
    if req.method == 'POST':
        form = BaseOrderForm(req.POST)
        if form.is_valid():
            oday, created = OrderDay.objects.get_or_create(day=date.today(),
                user=req.user)
            if created:
                oday.save()
            req.session['oday_id'] = oday.id
            art, created = Article.objects.get_or_create(
                name=form.cleaned_data['art_name'],
                ident=form.cleaned_data['art_id'],
                price=h.get_price(form.cleaned_data['art_price']))
            if created:
                art.quantity = form.cleaned_data['art_q']
                art.supplier = Company.objects.get(
                    id=form.cleaned_data['art_supplier_id'])
                art.save()
            order = Order.objects.create(count=form.cleaned_data['count'],
                article=art, order_day=oday)
            order.save()
            cost = Cost.objects.get(ident=4100)
            co = CostOrder.objects.create(percent=100, order=order,
                cost=cost)
            co.save()
            order.memo = form.cleaned_data['memo']
            order.for_test = form.cleaned_data['exam']
            order.for_repair = form.cleaned_data['repair']
            order.users.add(req.user)
            order.state = u'accepted'
            order.save()
            _orders.append(order.id)
            req.session['extra_orders'] = _orders
            messages.success(req, u'Ihre Bestellung %s wurde gespeichert.'
                             % order)
            return redirect('orders-extra-order')
        messages.error(req, u'Bitte füllen Sie die benötigten Felder aus.')
    else:
        form = BaseOrderForm()
    orders = Order.objects.select_related().filter(id__in=_orders).order_by(
        'article__name')
    ctx = dict(page_title=_(u'Extra Order'), form=form, menus=menus,
        article_id=article_id, extra=True, orders=orders, oday_id=oday_id)
    return render(req, 'orders/extra_order.html', ctx, app=u'orders')


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
    return render(req, 'orders/manage_orders.html', ctx, app=u'orders')


@any_permission_required(['orders.can_order', 'orders.can_change_orderstate'],
                         raise_exception=True)
def manage_order(req, oday_id):
    oday = OrderDay.objects.get(id=int(oday_id))
    for o in Order.objects.filter(count=0):
        o.delete()
    orders = Order.objects.select_related().filter(order_day=oday)
    order_sum = 0
    for o in orders:
        o.userlist = [x.username for x in o.users.all()]
        order_sum += o.count * o.article.price
        o.sum_price = o.count * o.article.price
        o.costlist = [u'%s: %d%%' % (unicode(x.cost), x.percent) for x in
                      CostOrder.objects.filter(order=o)]
    ctx = dict(page_title=_(u'Manage Orders'), menus=menus, oday=oday,
        orders=orders, states=(u'new', u'accepted', u'rejected'),
        order_sum=order_sum, suppliers=h.get_supplier_choices())
    return render(req, 'orders/manage_order.html', ctx, app=u'orders')


@permission_required('orders.can_order', raise_exception=True)
def add_oday(req):
    if req.method == 'POST':
        form = OrderDayForm(req.POST)
        form.fields['user'].choices = h.get_user_choices()
        if form.is_valid():
            if form.cleaned_data['user'].is_anonymous():
                messages.error(req, u'Der Benutzer ist nicht gültig.')
                return redirect('orders-manage')
            oday = OrderDay.objects.create(day=form.cleaned_data['day'],
                user=form.cleaned_data['user'])
            oday.save()
            messages.success(req,
                u'Neuer Bestelltag %s hinzugefügt.' % unicode(oday))
            return redirect('orders-manage')
        else:
            messages.error(req, u'Bitte korrigieren Sie das Formular.')
    else:
        form = OrderDayForm()
        form.fields['user'].choices = h.get_user_choices()
    odays = h.get_next_odays(True)
    ctx = dict(page_title=_(u'Add new orderday'), menus=menus, form=form,
        odays=[unicode(x) for x in odays])
    return render(req, 'orders/add_oday.html', ctx, app=u'orders')


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
    return render(req, 'orders/list_printouts.html', ctx, app=u'orders')


@login_required
def company_rating(req):
    average = None
    if req.method == 'POST':
        cid = int(req.POST.get('company_id'))
        form = CompanyRatingForm(req.POST, auto_id=False)
        if form.is_valid():
            company = Company.objects.get(id=cid)
            rating = CompanyRating.objects.create(company=company,
                user=req.user, **form.cleaned_data)
            rating.save()
            r, average = company.calculate_rating()
            messages.success(req, u'Bewertung wurde gespeichert.')
        else:
            messages.error(req, u'Bitte füllen Sie alle Pflichtfelder aus!')
    form = CompanyRatingForm(auto_id=False)
    companies = Company.objects.filter(rating_users=req.user)
    for c in companies:
        c.last_ratings = CompanyRating.objects.filter(user=req.user,
            company=c).order_by('-rated')
        c.average = c.calculate_rating()[1]
    ctx = dict(page_title=_(u'Company Rating'), menus=menus,
        companies=companies, form=form)
    return render(req, 'orders/ratings/rate.html', ctx, app=u'orders')


@permission_required('core.summarize', raise_exception=True)
def rate_company(req, company_id):
    company = Company.objects.get(id=int(company_id))
    if req.method == 'POST':
        if 'rate' in req.POST:
            sum_form = SummarizeForm(req.POST, instance=company)
            sum_form.save()
            messages.success(req, u'Gesamtbewertung gespeichert.')
        else:
            form = CompanyRatingForm(req.POST)
            if form.is_valid():
                rating = CompanyRating.objects.create(company=company,
                    user=req.user, **form.cleaned_data)
                rating.save()
                messages.success(req, u'Bewertung wurde gespeichert.')
    sum_form = SummarizeForm(instance=company)
    form = CompanyRatingForm()
    company = h.calculate_ratings([company])[0]
    ctx = dict(page_title=_(u'Edit Rating'), menus=menus, company=company,
        form=form, sum_form=sum_form)
    return render(req, 'orders/ratings/edit.html', ctx, app=u'orders')


@login_required
def company_rating_summary(req):
    companies = Company.objects.select_related().filter(rate=True
        ).order_by('name')
    companies = h.calculate_ratings(companies)
    ctx = dict(page_title=_(u'Company Rating Summary'), menus=menus,
        companies=companies, today=date.today())
    return render(req, 'orders/ratings/summary.html', ctx, app=u'orders')


@permission_required('core.summarize', raise_exception=True)
def manage_ratings(req):
    users = []
    for u in User.objects.exclude(username='admin').order_by('last_name'):
        u = h.get_company_data_for_rating_user(u)
        if hasattr(u, 'to_rate'):
            users.append(u)
    old_ratings = PDFPrintout.objects.filter(
        category=u'Lieferantenbewertung').order_by('-generated')
    companies = Company.objects.filter(rate=True).order_by('rating')
    ctx = dict(page_title=_(u'Manage Ratings'), menus=menus, users=users,
        uids=[x.id for x in users], old_ratings=old_ratings,
        companies=companies)
    return render(req, 'orders/ratings/manage.html', ctx, app=u'orders')


@permission_required('orders.controlling', raise_exception=True)
def ctrl_by_cost(req):
    ctx = dict(page_title=_(u'Sums by Cost'), menus=menus, costs=[],
        start=None, end=None)
    if req.method == 'POST':
        _start = req.POST.get('start', '')
        _end = req.POST.get('end', '')
        if not _start or not _end:
            start, end = h.get_dates()
        else:
            start = datetime.strptime(_start, '%d.%m.%Y').date()
            end = datetime.strptime(_end, '%d.%m.%Y').date()
        d = {}
        for c in CostOrder.objects.select_related().filter(
            order__ordered__gte=start, order__ordered__lte=end):
            price = Decimal(c.order.count) * c.order.article.price
            cost = (c.cost.short_name, c.cost.ident)
            if cost not in d:
                d[cost] = [Decimal(), Decimal(), 0]
            d[cost][0] += (c.percent / Decimal(100)) * price
            d[cost][1] += price
            d[cost][2] += 1
        l = sorted(((k, v) for k, v in d.iteritems()), key=lambda x: x[1])
        _ctx = dict(costs=l, start=start, end=end)
        ctx.update(_ctx)
    return render(req, 'orders/controlling/bycost.html', ctx, app=u'orders')
