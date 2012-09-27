# -*- coding: utf-8 -*-

from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from core.models import Company
from orders.models import OrderDay, Cost, Order, Article


def get_order_for_every_article():
    orders = []
    for art in Article.objects.all().order_by('name'):
        cond = {'article': art, 'state__in': [u'ordered', u'delivered']}
        try:
            order = Order.objects.select_related().filter(**cond
                ).latest('added')
            order.userlist = [x.username for x in order.users.all()]
            order.counts = 0
            order.sums = 0
            order.olist = []
            for o in Order.objects.filter(**cond).order_by('-ordered'):
                order.counts += o.count
                order.sums += o.price()
                order.olist.append(o.ordered)
            orders.append(order)
        except Order.DoesNotExist:
            pass
    return orders


def get_user_choices():
    return [(x.id, x.get_full_name() or x.username) for x in
            User.objects.all() if x.has_perm('orders.can_order')]


def get_supplier_choices():
    l = []
    for c in Company.objects.filter(rate=True).order_by('name'):
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


def get_dates():
    today = date.today()
    month, year = today.month, today.year
    if month == 1:
        start = date(year - 1, 12, 1)
        end = date(year - 1, 12, 31)
    else:
        start = date(year, month - 1, 1)
        end = date(year, month - 1, monthrange(year, month - 1)[1])
    return start, end


def calculate_ratings(companies):
    for c in companies:
        whole_ratings = defaultdict(int)
        collected = []
        for r in c.ratings.all():
            whole_ratings[r.rating] += 1
            collected.extend(r.as_list())
        tmp = [u'%dx %s' % (x, y) for x, y in sorted(whole_ratings.items(),
            key=lambda x: x[1])]
        c.whole_ratings = u', '.join(tmp)
        c.min_rating = min(collected)
        c.average = c.calculate_rating()[1]
    return companies
