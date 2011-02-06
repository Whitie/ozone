# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    (r'^$', 'index'),
    (r'^add_news/$', 'add_news'),
)
