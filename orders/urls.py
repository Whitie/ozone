# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('orders.views',
    url(r'^$', 'index', name='orders-index'),
    url(r'^detail/(?P<order_id>\d+)/$', 'order_detail', name='orders-detail'),
    url(r'^order/(?P<article_id>\d+)/$', 'order', name='orders-order'),
    url(r'^order/$', 'order', name='orders-order'),
    url(r'^add_supplier/$', 'add_supplier', name='orders-add-supplier'),
    url(r'^ask_order/$', 'ask_order', name='orders-ask'),
    url(r'^manage/$', 'manage_orders', name='orders-manage'),
    url(r'^myorders/$', 'myorders', name='orders-myorders'),
    url(r'^api/article/(?P<article_id>\d+)/$', 'api_article',
        name='orders-api-article'),
    url(r'^api/update_count/(?P<order_id>\d+)/(?P<count>\d+)/$',
        'update_article_count', name='orders-api-count'),
)
