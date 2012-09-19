# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('orders.views.web',
    url(r'^$', 'index', name='orders-index'),
    url(r'^detail/(?P<order_id>\d+)/$', 'order_detail', name='orders-detail'),
    url(r'^delete/(?P<oday_id>\d+)/(?P<order_id>\d+)/$', 'delete_order',
        name='orders-delete'),
    url(r'^order/(?P<article_id>\d+)/$', 'order', name='orders-order'),
    url(r'^order/$', 'order', name='orders-order'),
    url(r'^add/supplier/$', 'add_supplier', name='orders-add-supplier'),
    url(r'^add/orderday/$', 'add_oday', name='orders-add-oday'),
    url(r'^ask_order/$', 'ask_order', name='orders-ask'),
    url(r'^manage/$', 'manage_orders', name='orders-manage'),
    url(r'^manage/(?P<oday_id>\d+)/$', 'manage_order', name='orders-manage'),
    url(r'^myorders/$', 'myorders', name='orders-myorders'),
    url(r'^old/$', 'show_old_orders', name='orders-old'),
    url(r'^list/printouts/$', 'list_printouts', name='orders-list-printouts'),

    # Controlling
    url(r'^controlling/by_cost/$', 'ctrl_by_cost', name='orders-ctrl-bycost'),
)

urlpatterns += patterns('orders.views.delivery',
    url(r'^delivery/$', 'index', name='orders-delivery'),
)

urlpatterns += patterns('orders.views.ajax',
    # api
    url(r'^api/article/(?P<article_id>\d+)/$', 'api_article',
        name='orders-api-article'),
    url(r'^api/articles/get/$', 'get_articles', name='orders-api-articles'),
    url(r'^api/update_count/(?P<order_id>\d+)/(?P<count>\d+)/$',
        'update_article_count', name='orders-api-count'),
    url(r'^api/representative/$', 'add_representative',
        name='orders-api-repr'),
    url(r'^api/change_order/$', 'change_order', name='orders-api-change'),
    url(r'^api/delivery/$', 'update_delivery', name='orders-api-delivery'),
)

urlpatterns += patterns('orders.views.pdf',
    url(r'^generate_pdf/$', 'generate_pdf', name='orders-genpdf'),

    # api
    url(r'^api/generate_pdf/$', 'generate_one_pdf', name='orders-api-pdf'),
)
