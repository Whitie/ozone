# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from core.menu import Menu


order_menu = Menu(_(u'Orders'),
    ('orders-ask', _(u'Order now')),
    ('orders-myorders', _(u'My Orders')),
    ('orders-add-supplier', _(u'Add new Supplier')),
    ('orders-manage', _(u'Manage Orders')),
)

controlling_menu = Menu(_(u'Controlling'),
    ('orders-ctrl-bycost', _(u'By Cost')),
)

menus = [order_menu, controlling_menu]
