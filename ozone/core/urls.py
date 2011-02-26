# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('core.views',
    url(r'^$', 'index', name='core-index'),
    url(r'^add_news/$', 'add_news', name='core-add-news'),
    url(r'^login/$', 'do_login', name='core-login'),
    url(r'^logout/$', 'do_logout', name='core-logout'),
    url(r'^companies/$', 'list_companies', name='core-companies'),
    url(r'^companies/(?P<startchar>[A-Z])/$', 'list_companies'),
    url(r'^students/$', 'list_students', name='core-students'),
    url(r'^students/(?P<startchar>[A-Z])/$', 'list_students'),
    url(r'^groups/$', 'list_groups', name='core-groups'),
    url(r'^groups/(?P<gid>\d+)/$', 'group_details', name='core-group-details'),
    url(r'^students/archive/$', 'list_students', {'archive': True},
        name='core-students-archive'),
    url(r'^students/archive/(?P<startchar>[A-Z])/$', 'list_students',
        {'archive': True}),
    url(r'^barcode/(?P<barcode>.+)/$', 'barcode', name='barcode'),
)
