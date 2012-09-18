# -*- coding: utf-8 -*-

from decimal import Decimal

from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core.utils import json_view, json_rpc
from orders.models import Order, Article
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
def api_article(req, article_id=0):
    article_id = int(article_id)
    if not article_id:
        return {'count': 1}
    oday = h.get_next_odays()[0]
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
        msgs.append(u'%s hinzugefügt.' % u', '.join(added))
    if removed:
        msgs.append(u'%s entfernt.' % u', '.join(removed))
    return {'msg': u' '.join(msgs)}


@require_POST
@json_rpc
def change_order(req, data):
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
    msg = (u'Alle Änderungen an Bestellung: %(name)s (ID: %(id)d) '
           u'gespeichert.' % {'name': article.name, 'id': order_id})
    return {'msg': msg}
