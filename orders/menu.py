# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from core.menu import Menu


order_menu = Menu(_(u'Orders'),
    ('orders-ask', _(u'Order now')),
    ('orders-myorders', _(u'My Orders')),
    ('orders-add-supplier', _(u'Add new Supplier')),
)

menus = [order_menu]
