# -*- coding: utf-8 -*-

from decimal import Decimal
from smtplib import SMTPException
from urlparse import urljoin

from django.http import HttpResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.template import Context
from django.template.loader import get_template

from core.utils import json_view, json_rpc
from core.utils.cm_proxy import CMRpcProxy
from core.models import Company, CompanyRating
from core.forms import CompanyRatingForm
from orders.models import Order, Article, DeliveredOrder, OrderDay
from orders.views import helper as h


@json_view
def update_article_count(req, order_id, count):
    order_id, count = int(order_id), int(count)
    order = Order.objects.select_related().get(id=order_id)
    price = order.article.price_with_tax()
    old_count = order.count
    order.count = count
    new_price = count * price
    price_diff = new_price - old_count * price
    try:
        u = order.users.get(id=req.user.id)
    except:  # noqa: E722
        u = None
        order.users.add(req.user)
    order.save()
    msg = [u'Anzahl für %(name)s wurde von %(old)d auf %(count)d geändert.' %
           {'name': order.article.name, 'old': old_count, 'count': count}]
    if u is None:
        msg.append(u'Benutzer %s wurde hinzugefügt.' % req.user.username)
    user = [x.username for x in order.users.all()]
    return dict(
        msg=u' '.join(msg), user=u', '.join(user),
        price_diff=float(price_diff), new_price=float(new_price)
    )


@json_view
def get_articles(req):
    term = req.GET.get('term')
    query = Q(name__icontains=term) | Q(barcode__istartswith=term)
    query |= Q(ident__istartswith=term)
    articles = []
    for x in Article.objects.filter(query).order_by('name'):
        label = u'{0} ({1})'
        if x.discount_price:
            label += u' <b>RABATT</b>'
        articles.append({
            'value': x.id,
            'label': label.format(x.name, x.ident),
            'desc': x.short_desc()
        })
    return articles


@json_view
def get_article_by_barcode(req, barcode):
    code = h.extract_barcode(barcode)
    try:
        a = Article.objects.get(barcode=code)
    except Article.DoesNotExist:
        return dict(error=u'Artikel nicht gefunden!')
    return dict(id=a.id, artnr=a.ident, name=a.name, lieferant=a.supplier.name)


@json_view
def get_suppliers(req):
    term = req.GET.get('term')
    sup = [{'value': x.id, 'label': x.name} for x in Company.objects.filter(
        name__icontains=term, rate=True).order_by('name')]
    return sup


@require_POST
@json_rpc
def find_supplier(req, data):
    s = data['supp_name']
    supps = Company.objects.filter(
        Q(name__istartswith=s) | Q(name__icontains=s) | Q(name__iendswith=s)
    ).values_list('name', flat=True).order_by('name')
    return dict(supps=list(supps))


@json_view
def api_article(req, article_id=0):
    article_id = int(article_id)
    if not article_id:
        return {'count': 1}
    oday = h.get_next_odays()[0]
    a = Article.objects.get(pk=article_id)
    data = dict(
        art_name=a.name, art_supplier_id=a.supplier.id,
        art_id=a.ident, art_q=a.quantity, art_price=float(a.get_price()),
        count=1, oday=oday.id, art_supplier_name=a.supplier.short_name,
        art_tax=a.tax
    )
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
    try:
        supplier = Company.objects.get(id=data['supp_id'])
    except Company.DoesNotExist:
        supplier = None
    article = order.article
    old_price = article.price_with_tax() * order.count
    try:
        price = Decimal(data['price'].replace(u',', u'.'))
        article.name = data['art_name']
        article.ident = data['art_ident']
        article.price = price
    except KeyError:
        pass
    if supplier is not None:
        article.supplier = supplier
    article.save()
    order.count = data['count']
    order.save()
    total = article.price_with_tax() * order.count
    diff = total - old_price
    msg = (u'Alle Änderungen an Bestellung: %(name)s (ID: %(id)d) '
           u'gespeichert.' % {'name': article.name, 'id': order.id})
    return dict(msg=msg, diff=float(diff), total=float(total))


def _send_status_mail(user, order, template):
    for u in order.users.all():
        if u.email:
            tpl = get_template('orders/mail/' + template)
            ctx = dict(user=user, order=order, orderer=u)
            body = tpl.render(Context(ctx))
            send_mail(
                u'Statusänderung Ihrer Bestellung',
                body, 'dms@bbz-chemie.de', [u.email], fail_silently=False
            )


@require_POST
@json_rpc
def update_state(req, data):
    order = Order.objects.select_related().get(id=data['order_id'])
    old_state = order.state
    order.state = data['state']
    order.save()
    if old_state == u'rejected' and order.state in (u'new', u'accepted'):
        diff = order.count * order.article.price_with_tax()
    elif old_state in (u'new', u'accepted') and order.state == u'rejected':
        diff = order.count * order.article.price_with_tax() * -1
        try:
            _send_status_mail(req.user, order, u'order_rejected.txt')
        except Exception as e:
            print e
    else:
        diff = 0.0
    msg = (u'Status für %(art)s auf %(state)s gesetzt.' %
           {'art': order.article.name, 'state': order.get_state_display()})
    return dict(msg=msg, new_state=order.state, diff=float(diff))


def _notify_chemman(order, count):
    url = settings.get('CHEMMAN_URL', '')
    if not url:
        return
    user = settings.get('CHEMMAN_USER', '')
    pw = settings.get('CHEMMAN_PASSWORD', '')
    endpoint = urljoin(url, 'rpc/delivery/')
    data = {
        'ozone_id': order.article.id,
        'name': order.article.name,
        'ident': order.article.ident,
        'barcode': order.article.barcode,
        'quantity': order.article.quantity,
        'count': count,
    }
    proxy = CMRpcProxy(endpoint)
    proxy.authenticate(user, pw)
    return proxy.deliver(data)


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
            'u': dorder.user.userprofile}]
    if order.article.tox_control:
        try:
            _notify_chemman(order, data['count'])
            msg.append(u'Lieferung wurde an ChemManager übertragen.')
        except Exception:
            msg.append(
                u'Lieferung konnte nicht automatisch übertragen werden!')
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
               missing=missing, entry=entry,
               toxic=order.article.chemman)
    return ret


@require_POST
@json_rpc
def take_calculated_rating(req, data):
    company = Company.objects.get(id=data['company_id'])
    company.rating = data['rating']
    company.save()
    return {'msg': u'Bewertung gespeichert.'}


@require_POST
@json_rpc
def send_memory_mail(req, data):
    msg = []
    for uid in data['uids']:
        u = h.get_company_data_for_rating_user(User.objects.get(id=uid))
        t = get_template('orders/mail/company_rating.txt')
        body = t.render(Context({'user': u}))
        try:
            send_mail(u'Lieferantenbewertung', body, 'dms@bbz-chemie.de',
                      [u.email], fail_silently=False)
            msg.append(u'Mail an %s gesendet.' % u.email)
        except SMTPException:
            msg.append(u'Mail an %s konnte nicht gesendet werden.' % u.email)
    return {'msg': u' '.join(msg)}


@require_POST
@json_rpc
def check_supplier_id(req, data):
    try:
        Company.objects.get(id=data['sid'])
        return dict(result=True)
    except Company.DoesNotExist:
        return dict(result=False)


@require_POST
@json_rpc
def delete_order(req, data):
    order = Order.objects.get(id=data['oid'])
    try:
        order.delete()
        msg = u''
        ok = True
    except Exception as e:
        msg = u'Fehler beim Löschen: {0}'.format(unicode(e))
        ok = False
    return dict(msg=msg, ok=ok)


@json_rpc
def save_barcode(req, data):
    try:
        article = Article.objects.get(id=data['art_id'])
        article.barcode = data['barcode']
        article.save()
        return dict(msg=u'Barcode {0} gespeichert für Artikel {1}.'.format(
            article.barcode, article.name), saved=True)
    except Article.DoesNotExist:
        return dict(msg=u'Fehler! Barcode konnte nicht gespeichert werden.',
                    saved=False)


@json_rpc
def move_order(req, data):
    new_oday = OrderDay.objects.get(id=data['oday_id'])
    order = Order.objects.select_related().get(id=data['oid'])
    old_oday = order.order_day
    order.order_day = new_oday
    order.state = u'new'
    order.save()
    order.old_oday = old_oday
    _send_status_mail(req.user, order, 'order_moved.txt')
    return dict()


@json_rpc
def save_rating(req, data):
    cid = data.pop('company_id')
    company = Company.objects.get(id=int(cid))
    form = CompanyRatingForm(data)
    if form.is_valid():
        cd = form.cleaned_data
        rating = CompanyRating.objects.create(company=company,
                                              user=req.user, **cd)
        rating.save()
        msg = u'Bewertung wurde gespeichert.'
    else:
        msg = u'Fehler beim Speichern der Bewertung. Bitte wiederholen.'
    return dict(msg=msg)


def accept_oday(req, oday_id):
    if not req.user.has_perm('orders.can_accept_odays'):
        return HttpResponse('FAILED')
    oday = OrderDay.objects.get(id=int(oday_id))
    oday.accepted = True
    oday.save()
    return HttpResponse('OK')
