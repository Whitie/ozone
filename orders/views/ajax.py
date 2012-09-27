# -*- coding: utf-8 -*-

from decimal import Decimal

from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core.utils import json_view, json_rpc
from core.models import Company
from orders.models import Order, Article, DeliveredOrder
from orders.views import helper as h


@json_view
def update_article_count(req, order_id, count):
    order_id, count = int(order_id), int(count)
    order = Order.objects.select_related().get(id=order_id)
    old_count = order.count
    order.count = count
    try:
        u = order.users.get(id=req.user.id)
    except:
        u = None
        order.users.add(req.user)
    order.save()
    msg = [u'Anzahl für %(name)s wurde von %(old)d auf %(count)d geändert.' %
        {'name': order.article.name, 'old': old_count, 'count': count}]
    if u is None:
        msg.append(u'Benutzer %s wurde hinzugefügt.' % req.user.username)
    user = [x.username for x in order.users.all()]
    return dict(msg=u' '.join(msg), user=u', '.join(user))


@json_view
def get_articles(req):
    term = req.GET.get('term')
    articles = [{'value': x.id, 'label': x.name, 'desc': x.short_desc()}
                for x in Article.objects.filter(
                    name__icontains=term).order_by('name')]
    return articles


@json_view
def get_suppliers(req):
    term = req.GET.get('term')
    sup = [{'value': x.id, 'label': x.name} for x in Company.objects.filter(
        name__icontains=term, rate=True).order_by('name')]
    return sup


@json_view
def api_article(req, article_id=0):
    article_id = int(article_id)
    if not article_id:
        return {'count': 1}
    oday = h.get_next_odays()[0]
    a = Article.objects.get(pk=article_id)
    data = dict(art_name=a.name, art_supplier_id=a.supplier.id,
        art_id=a.ident, art_q=a.quantity, art_price=float(a.price),
        count=1, oday=oday.id, art_supplier_name=a.supplier.short_name)
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
        msgs.append(u'%s hinzugefügt.' % u', '.join(added))
    if removed:
        msgs.append(u'%s entfernt.' % u', '.join(removed))
    return {'msg': u' '.join(msgs)}


@require_POST
@json_rpc
def change_order(req, data):
    order = Order.objects.get(id=data['order_id'])
    supplier = Company.objects.get(id=data['supp_id'])
    article = order.article
    try:
        price = Decimal(data['price'].replace(u',', u'.'))
        article.name = data['art_name']
        article.ident = data['art_ident']
        article.price = price
    except KeyError:
        pass
    article.supplier = supplier
    article.save()
    order.count = data['count']
    if 'state' in data:
        order.state = data['state']
    order.save()
    msg = (u'Alle Änderungen an Bestellung: %(name)s (ID: %(id)d) '
           u'gespeichert.' % {'name': article.name, 'id': order.id})
    return {'msg': msg}


@require_POST
@json_rpc
def update_delivery(req, data):
    order = Order.objects.select_related().get(id=data['oid'])
    dorder = DeliveredOrder.objects.create(order=order, count=data['count'],
        user=req.user)
    dorder.save()
    dsum = 0
    for d in DeliveredOrder.objects.filter(order=order):
        dsum += d.count
    missing = order.count - dsum
    msg = [u'Wareneingang %(count)dx für %(art)s gespeichert von %(u)s.' %
           {'count': dorder.count, 'art': order.article.name,
            'u': dorder.user.get_profile()}]
    if not order.is_complete():
        msg.append(u'%dx fehlt noch.' % missing)
    else:
        msg.append(u'Bestellung ist komplett.')
        order.state = u'delivered'
        order.save()
    entry = u'<strong>%(count)dx</strong> %(date)s(%(u)s)<br />' % {
        'count': dorder.count,
        'date': dorder.date.strftime('%d.%m.%Y'),
        'u': dorder.user.username}
    ret = dict(msg=u' '.join(msg), complete=order.is_complete(),
        missing=missing, entry=entry)
    return ret
