# -*- coding: utf-8 -*-
# Create your views here.

import csv

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.db.models import Q

from core.utils import any_permission_required, render
from core.models import Company, CompanyRating, PDFPrintout
from core.forms import CompanyRatingForm
from orders.forms import (OrderForm, ShortSupplierForm,
                          OrderDayForm, BaseOrderForm, SummarizeForm)
from orders.models import (OrderDay, Order, Article, Cost, CostOrder, _mapper,
                           DeliveredOrder, STATE_CHOICES)
from orders.views import helper as h
from orders.menu import menus


# Views

def index(req):
    inc = req.user.has_perm('orders.can_order')
    odays = list(h.get_next_odays(inc))
    ctx = dict(page_title=u'Bestelltage', odays=odays, menus=menus)
    if odays:
        diff = odays[0].day - date.today()
        ctx['subtitle'] = u'Nächster in {0} Tag(en)'.format(diff.days)
    oday_count = len(odays)
    if oday_count < 2 and inc:
        if oday_count == 1:
            messages.warning(req, u'Es ist nur noch 1 Bestelltag angelegt!')
        else:
            messages.error(req, u'Es ist kein Bestelltag mehr angelegt!')
    if req.user.is_authenticated():
        deliveries = DeliveredOrder.objects.filter(order__users=req.user)
    else:
        deliveries = DeliveredOrder.objects.all()
    ctx['deliveries'] = deliveries.order_by('-date')[:5]
    return render(req, 'orders/index.html', ctx, app=u'orders')


@login_required
def show_old_orders(req):
    orders = h.get_order_for_every_article()
    try:
        first = Order.objects.all().order_by('added')[0]
        dt = first.added.strftime(settings.DEFAULT_DATE_FORMAT)
    except:  # noqa: E722
        dt = u''
    ctx = dict(page_title=_(u'All ordered articles'), menus=menus,
               orders=orders, dt=True, subtitle=u'Seit {0}'.format(dt))
    return render(req, 'orders/old_orders.html', ctx, app=u'orders')


@login_required
def order_detail(req, order_id):
    oid = int(order_id)
    oday = OrderDay.objects.get(id=oid)
    orders = Order.objects.select_related().filter(
        order_day=oday).order_by('-added', 'article__name')
    order_sum = 0
    for o in orders:
        o.userlist = [x.username for x in o.users.all()]
        o.costlist = [u'%s: %d%%' % (unicode(x.cost), x.percent) for x in
                      CostOrder.objects.filter(order=o)]
        order_sum += o.fullprice()
        o.netto = o.count * o.article.get_price()
        if (
            req.user.username in o.userlist
            and o.users.count() == 1
            and o.state in (u'new', u'accepted', u'rejected')
        ):
            o.deleteable = True
        else:
            o.deleteable = False
    ctx = dict(
        page_title=u'Offene Bestellungen', menus=menus, oday=oday,
        orders=orders, order_sum=order_sum, subtitle=unicode(oday), dt=True,
        need_ajax=True
    )
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
            cleaned = form.cleaned_data
            company = Company.objects.get(id=cleaned['art_supplier_id'])
            costs = h.get_costs(req.POST)
            art, created = h.search_article(
                cleaned['art_id'].strip(),
                cleaned['art_name'], cleaned['art_q'], company
            )
            art.tax = int(req.POST.get('tax', '19'))
            if created:
                art.tox_control = cleaned['tox']
                art.save()
            _price = h.get_price(cleaned['art_price'])
            if _price and art.price != _price:
                art.price = _price
                art.save()
            order = Order.objects.create(
                count=cleaned['count'], article=art,
                order_day=OrderDay.objects.get(id=int(cleaned['oday']))
            )
            order.save()
            for cost, percent in costs:
                co = CostOrder.objects.create(percent=percent, order=order,
                                              cost=cost)
                co.save()
            order.memo = cleaned['memo']
            order.for_test = cleaned['exam']
            order.for_repair = cleaned['repair']
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
    ctx = dict(
        page_title=_(u'New Order'), form=form, menus=menus, costs=costs,
        article_id=article_id, costs_msg=_(u'Sum of costs must be 100!'),
        cur_msg=u'Preis in %s.' % settings.CURRENCY[0], extra=False,
        need_ajax=True
    )
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


def _get_states():
    states = []
    for s, disp in STATE_CHOICES:
        states.append(
            dict(name=s, disp=disp, btn=_mapper[s][0], icon=_mapper[s][1])
        )
    return states


@login_required
def myorders(req, state=u'all'):
    if state == u'all':
        _orders = req.user.order_set.select_related().all()
    else:
        _orders = req.user.order_set.select_related().filter(state=state)
    orders = []
    ids = set()
    states = _get_states()
    _states = {x['name']: x for x in states}
    for o in _orders.order_by('article__name', '-added'):
        if (o.article.id, o.state) not in ids:
            ids.add((o.article.id, o.state))
            o.dsp_state = _states[o.state]
            orders.append(o)
    ctx = dict(
        page_title=_(u'My Orders'), dt=True, need_ajax=True,
        subtitle=unicode(req.user.userprofile),
        menus=menus, orders=orders, state=state, states=states
    )
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
            oday, created = OrderDay.objects.get_or_create(
                day=date.today(), user=req.user)
            if not created:
                oday.accepted = True
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
    ctx = dict(
        page_title=_(u'Extra Order'), form=form, menus=menus,
        article_id=article_id, extra=True, orders=orders, oday_id=oday_id
    )
    return render(req, 'orders/extra_order.html', ctx, app=u'orders')


@any_permission_required(['orders.can_order', 'orders.can_change_orderstate'],
                         raise_exception=True)
def manage_orders(req):
    if req.method == 'POST':
        day = int(req.POST['oday'])
        messages.warning(
            req, u'Alle Änderungen werden automatisch gespeichert!')
        return redirect('orders-manage', oday_id=day)
    users = User.objects.exclude(username='admin')
    can_order = [x.username for x in users if x.has_perm('orders.can_order')]
    can_change = [x.username for x in users
                  if x.has_perm('orders.can_change_orderstate')]
    limit = date.today() - timedelta(days=14)
    odays = OrderDay.objects.filter(day__gte=limit).order_by('day')
    ctx = dict(
        page_title=_(u'Manage Orders'), menus=menus, odays=odays,
        users=users, can_order=can_order, can_change=can_change,
        need_ajax=True
    )
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
        if o.state in (u'new', u'accepted'):
            order_sum += o.fullprice()
        o.sum_price = o.count * o.article.get_price()
        o.costlist = [u'%s: %d%%' % (unicode(x.cost), x.percent) for x in
                      CostOrder.objects.filter(order=o)]
    ctx = dict(
        page_title=u'Bestellungen bearbeiten', menus=menus, oday=oday,
        subtitle=u'für {0}'.format(unicode(oday)), need_ajax=True, dt=True,
        orders=orders, states=(u'new', u'accepted', u'rejected'),
        order_sum=order_sum, suppliers=h.get_supplier_choices()
    )
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
            oday = OrderDay.objects.create(
                day=form.cleaned_data['day'],
                user=form.cleaned_data['user'], accepted=False
            )
            oday.save()
            messages.success(
                req, u'Neuer Bestelltag %s hinzugefügt.' % unicode(oday)
            )
            return redirect('orders-add-oday')
        else:
            messages.error(req, u'Bitte korrigieren Sie das Formular.')
    else:
        form = OrderDayForm()
        form.fields['user'].choices = h.get_user_choices()
    odays = h.get_next_odays(True)
    ctx = dict(page_title=_(u'Add new orderday'), menus=menus, form=form,
               odays=[unicode(x) for x in odays], dp=True)
    return render(req, 'orders/add_oday.html', ctx, app=u'orders')


@permission_required('orders.can_order', raise_exception=True)
def list_printouts(req):
    odays = OrderDay.objects.select_related().all().order_by('-day')
    for oday in odays:
        oday.price = 0
        oday.count = 0
        for o in oday.orders.all():
            oday.price += o.fullprice()
            oday.count += 1
    ctx = dict(
        page_title=_(u'List of all printouts'),
        subtitle=_(u'By orderday'), menus=menus, odays=odays
    )
    return render(req, 'orders/list_printouts.html', ctx, app=u'orders')


# Generate CSV files to upload on supplier website
@permission_required('orders.can_order', raise_exception=True)
def generate_csv(req, supplier_id, oday_id):
    supp = Company.objects.get(id=int(supplier_id))
    oday = OrderDay.objects.get(id=int(oday_id))
    orders = Order.objects.select_related().filter(
        order_day=oday, state__in=[u'accepted', u'ordered'],
        article__supplier=supp
    )
    response = HttpResponse(content_type='text/csv')
    company = supp.short_name or unicode(supp.id)
    dt = oday.day.strftime('%Y%m%d')
    filename = u'%s_%s.csv' % (company, dt)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response, delimiter=';')
    for order in orders:
        if supp.id == 33:
            row = [
                order.article.ident.encode('utf-8'),
                'ea',
                str(order.count)
            ]
        else:
            row = [
                order.article.ident.encode('utf-8'),
                str(order.count)
            ]
        writer.writerow(row)
    return response


@login_required
def company_rating(req):
    companies = Company.objects.filter(rating_users=req.user)
    for c in companies:
        c.last_ratings = CompanyRating.objects.filter(
            user=req.user, company=c).order_by('-rated')
        c.average = c.calculate_rating()[1]
    ctx = dict(
        page_title=u'Lieferantenbewertung', menus=menus,
        companies=companies, subtitle=unicode(req.user.userprofile),
        need_ajax=True
    )
    return render(req, 'orders/ratings/rate.html', ctx, app=u'orders')


@login_required
def show_rate_form(req, cid):
    form = CompanyRatingForm()
    company = Company.objects.get(id=int(cid))
    ctx = dict(form=form, company=company)
    return render(req, 'orders/ratings/form_dlg.html', ctx, app=u'orders')


@login_required
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
                rating = CompanyRating.objects.create(
                    company=company, user=req.user, **form.cleaned_data)
                rating.save()
                messages.success(req, u'Bewertung wurde gespeichert.')
    sum_form = SummarizeForm(instance=company)
    form = CompanyRatingForm()
    company = h.calculate_ratings([company])[0]
    ctx = dict(
        page_title=u'Bewertung bearbeiten', menus=menus,
        company=company, form=form, sum_form=sum_form, subtitle=company.name
    )
    return render(req, 'orders/ratings/edit.html', ctx, app=u'orders')


@login_required
def company_rating_summary(req):
    companies = Company.objects.select_related().filter(
        rate=True).order_by('name')
    companies = h.calculate_ratings(companies)
    today = date.today()
    ctx = dict(
        page_title=u'Lieferantenbewertung', menus=menus, dt=True,
        companies=companies, need_ajax=True,
        subtitle=today.strftime('Zusammenfassung %m/%Y')
    )
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
    ctx = dict(
        page_title=u'Bewertungen verwalten', menus=menus, users=users,
        uids=[x.id for x in users], old_ratings=old_ratings,
        companies=companies, need_ajax=True
    )
    return render(req, 'orders/ratings/manage.html', ctx, app=u'orders')


# @permission_required('orders.controlling', raise_exception=True)
@login_required
def ctrl_by_cost(req):
    ctx = dict(page_title=u'Nach Kostenstellen', menus=menus, costs=[],
               start=None, end=None, dp=True, dt=True)
    if req.method == 'POST':
        _start = req.POST.get('start', '')
        _end = req.POST.get('end', '')
        if not _start or not _end:
            start, end = h.get_dates()
        else:
            start = datetime.strptime(_start, '%d.%m.%Y').date()
            end = datetime.strptime(_end, '%d.%m.%Y').date()
        d = {}
        whole = Decimal()
        chem = Decimal()
        for c in CostOrder.objects.select_related().filter(
          order__ordered__gte=start, order__ordered__lte=end):
            price = Decimal(c.order.count) * c.order.article.price
            weighted = (c.percent / Decimal(100)) * price
            whole += weighted
            if c.order.article.tox_control:
                chem += weighted
            cost = (c.cost.short_name, c.cost.ident)
            if cost not in d:
                d[cost] = [Decimal(), 0, 0]
            d[cost][0] += weighted
            d[cost][1] += 1
        for cost, prices in d.items():
            d[cost][2] = (prices[0] / whole) * 100
        costs = sorted(
            ((k, v) for k, v in d.iteritems()), key=lambda x: x[0][1]
        )
        if not costs:
            messages.error(
                req, u'Keine Bestellungen in dieser Zeitspanne gefunden.'
            )
            return redirect('orders-ctrl-bycost')
        _ctx = dict(costs=costs, start=start, end=end, whole=whole, chem=chem,
                    subtitle=u'{:%d.%m.%Y} - {:%d.%m.%Y}'.format(start, end))
        ctx.update(_ctx)
    return render(req, 'orders/controlling/bycost.html', ctx, app=u'orders')


def move_order(req):
    oday = OrderDay.objects.get(id=int(req.GET.get('oday_id')))
    order = Order.objects.get(id=int(req.GET.get('oid')))
    odays = OrderDay.objects.filter(day__gt=oday.day).order_by('day')
    ctx = dict(odays=odays, oday=oday, order=order)
    return render(req, 'orders/move_order.html', ctx)


@login_required
def database_maintenance(req):
    known = set()
    articles = []
    for art in Article.objects.all():
        if art.ident.upper() not in known:
            known.add(art.ident.upper())
            tmp = [art]
            q = Q(ident__iexact=art.ident)
            q |= Q(ident__icontains=art.ident) & Q(name__icontains=art.name)
            for a in Article.objects.exclude(id=art.id).filter(q):
                tmp.append(a)
            if len(tmp) > 1:
                articles.append((art, tmp))
    ctx = dict(
        page_title=u'Finde doppelte Artikel', menus=menus,
        articles=articles, subtitle=u'{0} vorhanden'.format(len(articles))
    )
    return render(req, 'orders/db_maintenance.html', ctx, app=u'orders')


def delete_articles(req):
    if not req.user.is_superuser:
        messages.error(req, u'Sie dürfen keine Artikel löschen!')
        return redirect('orders-admin-db')
    keep = int(req.POST.get('keep'))
    delete = map(int, req.POST.getlist('delete'))
    edit = int(req.POST.get('edit', 0))
    if keep in delete:
        delete.remove(keep)
    art = Article.objects.get(id=keep)
    counter = 0
    for o in Order.objects.filter(article__id__in=delete):
        o.article = art
        o.save()
        counter += 1
    messages.info(req, u'{0} Bestellung(en) wurde(n) geändert.'.format(
        counter))
    q = Article.objects.filter(id__in=delete)
    counter = q.count()
    q.delete()
    messages.info(req, u'{0} Artikel wurde(n) gelöscht.'.format(counter))
    if edit:
        return redirect('admin:orders_article_change', art.id)
    return redirect('orders-admin-db')
