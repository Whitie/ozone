# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler500 = 'core.utils.internal_server_error'

urlpatterns = patterns('',
    (r'^$', 'core.views.web.index'),
    (r'^core/', include('core.urls')),
    (r'^orders/', include('orders.urls')),
#    (r'^desktop/', include('desktop.urls')),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^favicon\.ico$', RedirectView.as_view(
            url='/static/img/favicon.ico')),
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
