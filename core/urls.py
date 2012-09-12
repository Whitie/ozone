# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns('core.views',
    # Common views
    url(r'^$', 'index', name='core-index'),
    url(r'^add_news/$', 'add_news', name='core-add-news'),
    url(r'^birthdays/$', 'get_next_birthdays', name='core-birthdays'),
    url(r'^profile/$', 'edit_profile', name='core-profile'),
    url(r'^phonelist/$', 'internal_phonelist', name='core-phonelist'),
    url(r'^login/$', 'do_login', name='core-login'),
    url(r'^logout/$', 'do_logout', name='core-logout'),
    # Companies
    url(r'^companies/$', 'list_companies', name='core-companies'),
    url(r'^companies/list_all/$', 'list_all_companies',
        name='core-companies-all', kwargs={'only_with_students': False}),
    url(r'^companies/list_with_students/$', 'list_all_companies',
        name='core-companies-with-students',
        kwargs={'only_with_students': True}),
    url(r'^companies/(?P<id>\d+)/$', 'company_details',
        name='core-company-detail'),
    url(r'^companies/(?P<startchar>[A-Z])/$', 'list_companies'),
    url(r'^companies/addnote/(?P<id>\d+)/$', 'add_note',
        name='core-company-addnote'),
    # Students
    url(r'^students/$', 'list_students', name='core-students'),
    url(r'^students/(?P<startchar>[A-Z])/$', 'list_students'),
    url(r'^students/all/$', 'list_all_students', name='core-students-all'),
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
    url(r'^presence/edit/(?P<student_id>\d+)/$', 'presence_edit',
        name='core-presence-edit'),
    url(r'^presence/printouts/(?P<job>[A-Z][a-z]+)/$', 'presence_printouts',
        name='core-presence-printouts'),
    # Barcode generation (not used yet)
    url(r'^barcode/(?P<format>[a-z]{3,4})/(?P<barcode>.+)/$', 'barcode',
        name='barcode'),
)

# JSON API
urlpatterns += patterns('core.json_views',
    url(r'^api/presence/update/$', 'update_presence',
        name='core-api-presence-update'),
    url(r'^api/presence/update_day/$', 'update_day',
        name='core-api-presence-update-day'),
)

# PDF generation
urlpatterns += patterns('core.pdf_views',
    url(r'^pdf/test/$', 'pdf', name='core-pdfgen'),
    url(r'^pdf/presence/clean/(?P<gid>\d+)/'
        r'(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'generate_presence_clean',
        name='core-pdf-presence-clean'),
    url(r'^pdf/presence/filled/(?P<gid>\d+)/'
        r'(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'generate_presence_filled',
        name='core-pdf-presence'),
    url(r'^api/presence/pdf/$', 'generate_presence_pdf',
        name='core-api-pdf-presence'),
)
