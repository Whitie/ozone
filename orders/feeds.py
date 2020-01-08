# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from orders.models import Order, DeliveredOrder


class LatestOrdersFeed(Feed):
    title = _(u'Latest Orders')
    link = '/orders/'
    description = _(u'Shows the last 10 orders made.')

    def items(self):
        return Order.objects.order_by('-added')[:10]

    def item_title(self, item):
        title = u'{article}, {date}'.format(
            article=unicode(item.article),
            date=item.added.strftime(settings.DEFAULT_DATETIME_FORMAT)
        )
        return title

    def item_description(self, item):
        desc = u'Bestellung: {order}, Status: {state}'.format(
            order=unicode(item), state=item.get_state_display())
        return desc

    def item_link(self, item):
        return reverse('orders-detail', kwargs={'order_id': item.order_day.id})


class LatestDeliveriesFeed(Feed):
    title = _(u'Latest Deliveries')
    link = '/orders/delivery/'
    description = _(u'Shows the last 20 deliveries.')

    def items(self):
        return DeliveredOrder.objects.order_by('-date')[:20]

    def item_title(self, item):
        title = u'{date}, Artikel: {article}'.format(
            date=item.date.strftime(settings.DEFAULT_DATE_FORMAT),
            article=unicode(item.order.article))
        return title

    def item_description(self, item):
        if item.order.is_complete():
            comp = u', Bestellung vollständig.'
        else:
            comp = u', UNVOLLSTÄNDIG.'
        data = dict(
            ocount=item.order.count,
            odate=item.order.ordered.strftime(settings.DEFAULT_DATE_FORMAT),
            users=u', '.join([x.username for x in item.order.users.all()]),
            count=item.count,
            date=item.date.strftime(settings.DEFAULT_DATE_FORMAT),
            comp=comp,
        )
        desc = (u'Bestellt: {ocount}x {odate} von {users}, geliefert: '
                u'{count}x {date}{comp}'.format(**data))
        return desc

    def item_link(self, item):
        return reverse('orders-delivery')


class LatestUserDeliveriesFeed(LatestDeliveriesFeed):
    title = _(u'My Latest Deliveries')

    def get_object(self, req, user_id):
        return User.objects.get(pk=int(user_id))

    def description(self, obj):
        return _(u'Latest 10 deliveries for {0}.'.format(
            unicode(obj.userprofile)))

    def items(self, obj):
        return DeliveredOrder.objects.filter(order__users=obj).order_by(
            '-date')[:10]
