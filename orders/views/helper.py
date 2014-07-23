# -*- coding: utf-8 -*-

import re

from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from core.models import Company, CompanyRating
from orders.models import OrderDay, Cost, Order, Article


UNIT = r'(?P<unit>[a-zµ]+)'
CALC_re = re.compile(
    r'(?P<count>\d+)\s*?x\s*?(?P<value>\d+)\s*?' + UNIT, re.I | re.U
)
FLOAT_re = re.compile(
    r'(?P<value>\d+[\.,]\d+)\s*?' + UNIT, re.I | re.U
)
INT_re = re.compile(
    r'(?P<value>\d+)\s*?' + UNIT, re.I | re.U
)


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
    if isinstance(value, Decimal):
        return value
    else:
        value = str(value)
    if not value.strip():
        return Decimal('0.0')
    value = value.strip().replace(u',', u'.')
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
        notes = []
        for r in c.ratings.all():
            whole_ratings[r.rating] += 1
            collected.extend(r.as_list())
            if r.note:
                notes.append(u'%s: %s' % (r.user.last_name, r.note))
        sratings = sorted(whole_ratings.items(), key=lambda x: x[1])
        tmp = [u'%dx %s' % (y, x) for x, y in sratings]
        c.whole_ratings = u', '.join(tmp)
        try:
            c.min_rating = min(collected)
        except ValueError:
            c.min_rating = u'-'
        c.calculated, c.average = c.calculate_rating()
        c.raterlist = [x.last_name for x in c.rating_users.all()]
        c.rating_notes = notes
    return companies


def get_company_data_for_rating_user(user):
    companies = Company.objects.filter(rating_users=user, rate=True)
    if companies:
        for c in companies:
            try:
                r = CompanyRating.objects.filter(company=c, user=user
                    ).latest('rated')
                c.last_rate = r.rated
            except CompanyRating.DoesNotExist:
                c.last_rate = None
        user.to_rate = companies
    return user


def extract_barcode(code):
    code_lower = code.strip('\r\n ').lower()
    if code_lower.startswith('roth'):
        # Roth
        for c in code.split('!'):
            if u'.' in c and len(c) > 4:
                return c.upper()
    if u',' in code_lower or u';' in code_lower:
        # Maybe Sigma Aldrich, Th. Geyer, Machery-Nagel
        if u',' in code_lower:
            c = code_lower.split(u',')[0].strip()
        else:
            c = code_lower.split(u';')[0].strip()
            # Machery-Nagel
            if c.startswith(u'91'):
                try:
                    Article.objects.get(ident=c[2:])
                    c = c[2:]
                except Article.DoesNotExist:
                    pass
        return c.upper()
    return code


_clean_unit = lambda unit: unit.replace(u'Liter', u'L')


def split_unit(value):
    m = CALC_re.search(value)
    if m is not None:
        val = int(m.group('count')) * Decimal(m.group('value'))
        return val, _clean_unit(m.group('unit'))
    m = FLOAT_re.search(value)
    if m is not None:
        val = m.group('value').replace(u',', u'.')
        return Decimal(val), _clean_unit(m.group('unit'))
    m = INT_re.search(value)
    if m is not None:
        val = Decimal(m.group('value'))
        return val, _clean_unit(m.group('unit'))
    return 1, value


def search_article(article_id, name, company):
    try:
        article = Article.objects.get(supplier=company,
            ident__iexact=article_id)
        return article, False
    except Article.DoesNotExist:
        pass
    for lookup in ('name__iexact', 'name__istartswith', 'name__icontains'):
        tmp = {'supplier': company, lookup: name}
        try:
            articles = Article.objects.filter(**tmp)
            return articles.first(), False
        except Article.DoesNotExist:
            pass
    article = Article.objects.create(supplier=company, ident=article_id,
        name=name)
    return article, True
