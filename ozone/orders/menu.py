# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from core.menu import Menu


order_menu = Menu(_(u'Orders'),
    ('orders-index', _(u'Main')),
)

menus = [order_menu]
