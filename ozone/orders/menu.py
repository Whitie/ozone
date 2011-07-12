# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from core.menu import Menu


order_menu = Menu(_(u'Orders'),
    ('orders-order-old', _(u'Order now')),
    ('orders-myorders', _(u'My Orders')),
)

menus = [order_menu]
