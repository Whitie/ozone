# -*- coding: utf-8 -*-

from django.conf.urls import *


urlpatterns = patterns('core.views.web',
    # Common views
    url(r'^$', 'index', name='core-index'),
    url(r'^add_news/$', 'add_news', name='core-add-news'),
    url(r'^birthdays/$', 'get_next_birthdays', name='core-birthdays'),
    url(r'^profile/$', 'edit_profile', name='core-profile'),
    url(r'^phonelist/$', 'internal_phonelist', name='core-phonelist'),
    url(r'^login/$', 'do_login', name='core-login'),
    url(r'^logout/$', 'do_logout', name='core-logout'),
    url(r'^internal_admin/$', 'internal_admin', name='core-admin'),
    # Companies
    url(r'^companies/$', 'list_companies', name='core-companies'),
    url(r'^companies/list_all/$', 'list_all_companies',
        name='core-companies-all', kwargs={'only_with_students': False}),
    url(r'^companies/list_with_students/$', 'list_all_companies',
        name='core-companies-with-students',
        kwargs={'only_with_students': True}),
    url(r'^companies/(?P<company_id>\d+)/$', 'company_details',
        name='core-company-detail'),
    url(r'^companies/(?P<startchar>[A-Z])/$', 'list_companies',
        name='core-companies'),
    url(r'^companies/addnote/(?P<id>\d+)/$', 'add_note',
        name='core-company-addnote'),
    # Students
    url(r'^students/$', 'list_students', name='core-students'),
    url(r'^students/(?P<startchar>[A-Z])/$', 'list_students',
        name='core-students'),
    url(r'^students/all/$', 'list_all_students', name='core-students-all'),
    url(r'^students/search/$', 'search_student', name='core-students-search'),
    url(r'^student/edit/(?P<sid>\d+)/$', 'edit_student',
        name='core-student-edit'),
    # Student groups
    url(r'^groups/$', 'list_groups', name='core-groups'),
    url(r'^groups/(?P<gid>\d+)/$', 'group_details', name='core-group-details'),
    # Collegues
    url(r'^colleagues/$', 'list_colleagues', name='core-colleagues'),
    url(r'^colleagues/add/$', 'add_colleague', name='core-user-add'),
    url(r'^colleagues/info/(?P<uid>\d+)/$', 'get_user_info'),
    url(r'^colleagues/filter/(?P<filter>all|internal|external)/$',
        'filter_colleagues', name='core-colleagues-filter'),
    # Archive
    url(r'^students/archive/$', 'list_students', {'archive': True},
        name='core-students-archive'),
    url(r'^students/archive/(?P<startchar>[A-Z])/$', 'list_students',
        {'archive': True}, name='core-students-archive'),
    # Presence management
    url(r'^presence/$', 'presence_overview', name='core-presence'),
    url(r'^presence/group/(?P<gid>\d+)/$', 'presence_for_group',
        name='core-presence-group'),
    url(r'^presence/edit/(?P<student_id>\d+)/$', 'presence_edit',
        name='core-presence-edit'),
    url(r'^presence/printouts/(?P<job>.+)/$', 'presence_printouts',
        name='core-presence-printouts'),
    url(r'^my_presence/select_groups/$', 'select_groups',
        name='core-presence-select-groups'),
    url(r'^my_presence/mystudents/$', 'mystudents',
        name='core-presence-mystudents'),
    url(r'^my_presence/list/$', 'mypresence', name='core-presence-own'),
    # Accidents
    url(r'^accidents/$', 'accidents_index', name='core-accidents'),
    url(r'^accidents/(?P<id>\d+)/$', 'accident_details',
        name='core-accident-details'),
    url(r'^accidents/statistics/$', 'accidents_statistics',
        name='core-accidents-statistic'),
    url(r'^accidents/add/$', 'accident_add', name='core-accident-add'),
    # Excel integration
    url(r'^group/export_excel/(?P<gid>\d+)/$', 'export_group_excel',
        name='core-group-to-excel'),
    # JSON Export
    url(r'^group/export_json/(?P<gid>\d+)/$', 'export_group_json',
        name='core-group-to-json'),
    # Barcode generation (not used yet)
    url(r'^barcode/(?P<format>[a-z]{3,4})/(?P<barcode>.+)/$', 'barcode',
        name='barcode'),
)

# Add students
urlpatterns += patterns('core.views.add_student',
    url(r'student/add/$', 'student_wizard_view_wrapper',
        name='core-student-add'),
    url(r'student/added/(?P<student_id>\d+)/$', 'student_added',
        name='core-student-added'),
)

# Journal
urlpatterns += patterns('core.views.journal',
    url(r'^journal/myentries/$', 'my_entries', name='core-myentries'),
    url(r'^journal/$', 'list_journals', name='core-journals'),
    url(r'^journal/media/(?P<entry_id>\d+)/$', 'show_media_for_entry',
        name='core-entry-media'),
    url(r'^journal/entry/add/(?P<gid>\d+)/$', 'add_entry',
        name='core-add-entry'),
    url(r'^journal/add/$', 'add_journal', name='core-add-journal'),
    url(r'^journal/rights/(?P<jid>\d+)/$', 'edit_rights',
        name='core-journal-rights'),
)

# JSON API
urlpatterns += patterns('core.views.ajax',
    url(r'^api/presence/update/$', 'update_presence',
        name='core-api-presence-update'),
    url(r'^api/presence/update_day/$', 'update_day',
        name='core-api-presence-update-day'),
    url(r'^api/journal/student_data/$', 'get_entries_for_student',
        name='core-api-student-entries'),
    url(r'^api/iadmin/clean_sessions/$', 'clean_sessions',
        name='core-api-clean-sessions'),
    url(r'^api/iadmin/clean_presence/$', 'clean_presence',
        name='core-api-clean-presence'),
    url(r'^api/iadmin/migrate30/', 'migrate30', name='core-api-migrate30'),
    url(r'^api/iadmin/clean_build_dir/$', 'clean_build_dir',
        name='core-api-clean-build-dir'),
    url(r'^api/student/delete/$', 'delete_student'),
    url(r'^api/company/contracts/$', 'get_contracts',
        name='core-api-contracts'),
    url(r'^api/student/save/$', 'save_student', name='core-api-student-save'),
    url(r'^api/presence/mygroups/$', 'mygroups',
        name='core-api-presence-mygroups'),
    url(r'^api/presence/mystudent/$', 'mystudent',
        name='core-api-presence-mystudent'),
    url(r'^api/accidents/save/$', 'save_accident',
        name='core-api-accident-save'),
    url(r'^api/presence/delete_own_list/$', 'delete_own_list',
        name='core-api-delete-own-presence'),
)

# PDF generation
urlpatterns += patterns('core.views.pdf',
    url(r'^pdf/test/$', 'pdf', name='core-pdfgen'),
    url(r'^pdf/presence/clean/(?P<gid>\d+)/'
        r'(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'generate_presence_clean',
        name='core-pdf-presence-clean'),
    url(r'^pdf/presence/filled/(?P<gid>\d+)/'
        r'(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'generate_presence_filled',
        name='core-pdf-presence'),
    url(r'^api/presence/pdf/$', 'generate_presence_pdf',
        name='core-api-pdf-presence'),
    url(r'^api/presence/pdf/all/$', 'generate_presence_pdf_all',
        name='core-api-pdf-presence-all'),
    url(r'^pdf/phonelist/$', 'generate_phonelist', name='core-pdf-phonelist'),
    url(r'^pdf/student/detail/(?P<sid>\d+)/$', 'student_detail',
        name='core-pdf-student-detail'),
)
