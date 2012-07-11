# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('core.views',
    # Common views
    url(r'^$', 'index', name='core-index'),
    url(r'^add_news/$', 'add_news', name='core-add-news'),
    url(r'^login/$', 'do_login', name='core-login'),
    url(r'^logout/$', 'do_logout', name='core-logout'),
    # Companies
    url(r'^companies/$', 'list_companies', name='core-companies'),
    url(r'^companies/(?P<id>\d+)/$', 'company_details',
        name='core-company-detail'),
    url(r'^companies/(?P<startchar>[A-Z])/$', 'list_companies'),
    url(r'^companies/addnote/(?P<id>\d+)/$', 'add_note',
        name='core-company-addnote'),
    # Students
    url(r'^students/$', 'list_students', name='core-students'),
    url(r'^students/(?P<startchar>[A-Z])/$', 'list_students'),
    # Student groups
    url(r'^groups/$', 'list_groups', name='core-groups'),
    url(r'^groups/(?P<gid>\d+)/$', 'group_details', name='core-group-details'),
    # Archive
    url(r'^students/archive/$', 'list_students', {'archive': True},
        name='core-students-archive'),
    url(r'^students/archive/(?P<startchar>[A-Z])/$', 'list_students',
        {'archive': True}),
    # Presence management
    url(r'^presence/$', 'presence_overview', name='core-presence'),
    url(r'^presence/group/(?P<gid>\d+)/$', 'presence_for_group',
        name='core-presence-group'),
    url(r'^presence/add/(?P<student_id>\d+)/$', 'presence_add',
        name='core-presence-add'),
    # Barcode generation (not used yet)
    url(r'^barcode/(?P<format>[a-z]{3,4})/(?P<barcode>.+)/$', 'barcode',
        name='barcode'),
)

# PDF generation (not used yet)
urlpatterns += patterns('core.pdf_views',
    url(r'^pdf/$', 'pdf', name='core-pdfgen'),
)
