# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from core.menu import Menu


order_menu = Menu(_(u'Orders'),
    ('orders-ask', _(u'Order now')),
    ('orders-myorders', _(u'My Orders')),
    ('orders-old', _(u'Old Orders')),
    ('orders-add-supplier', _(u'Add new Supplier')),
    ('orders-extra-order', _(u'Extra Order')),
    ('orders-delivery', _(u'Delivery')),
    ('orders-csv-export', u'Toxolution Export'),
    ('orders-manage', _(u'Manage Orders')),
)

controlling_menu = Menu(_(u'Controlling'),
    ('orders-ctrl-bycost', _(u'By Cost')),
)

rating_menu = Menu(_(u'Company Rating'),
    ('orders-rating', _(u'Rate')),
    ('orders-rating-summary', _(u'Summary')),
    ('orders-rating-manage', _(u'Manage')),
)

menus = [order_menu, rating_menu, controlling_menu]
