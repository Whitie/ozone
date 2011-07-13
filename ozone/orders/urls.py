# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('orders.views',
    url(r'^$', 'index', name='orders-index'),
    url(r'^detail/(?P<order_id>\d+)/$', 'order_detail', name='orders-detail'),
    url(r'^order/(?P<article>\d+)/$', 'order', name='orders-order'),
    url(r'^order/$', 'order', name='orders-order'),
    url(r'^ask_order/$', 'ask_order', name='orders-ask'),
    url(r'^myorders/$', 'myorders', name='orders-myorders'),
)
