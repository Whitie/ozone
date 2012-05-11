# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'core.views.index'),
    (r'^core/', include('core.urls')),
    (r'^orders/', include('orders.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to',
     {'url': '/static/img/favicon.ico'}),

    # Only for Testing!!!
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
)
