# -*- coding: utf-8 -*-

from django.contrib import admin
from core.models import *


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name_prefix', 'lastname', 'firstname', 'company',
                    'function', 'phone', 'email')
    list_display_links = ('lastname', 'company')
    list_editable = ('function', 'phone', 'email')
    list_filter = ('company',)
    ordering = ('lastname',)
    save_on_top = True
    search_fields = ('lastname', 'email', 'company__name')


class ContactInline(admin.StackedInline):
    model = Contact
    max_num = 5
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    inlines = (ContactInline,)
    list_display = ('name', 'short_name', 'phone', 'fax', 'customer_number',
                    'qm_rating')
    list_display_links = ('name', 'short_name')
    list_editable = ('phone', 'fax')
    list_filter = ('qm_rating',)
    ordering = ('name',)
    save_on_top = True
    search_fields = ('name', 'short_name', 'zip_code')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('group', 'company', 'lastname', 'firstname', 'birthdate',
                    'phone', 'email')
    list_display_links = ('lastname',)
    list_editable = ('phone', 'email')
    list_filter = ('group', 'company')
    save_on_top = True
    search_fields = ('lastname', 'company__name', 'group__job_short')


class StudentInline(admin.StackedInline):
    model = Student
    max_num = 20
    extra = 3


class StudentGroupAdmin(admin.ModelAdmin):
    inlines = (StudentInline,)
    list_display = ('__unicode__', 'job', 'start_date', 'finished')
    list_display_links = ('__unicode__', 'job')
    list_editable = ('finished',)
    list_filter = ('finished',)
    save_on_top = True
    search_fields = ('job', 'job_short')


class MemoAdmin(admin.ModelAdmin):
    list_display = ('created_by', '__unicode__')
    list_display_links = ('created_by',)
    search_fields = ('created_by__last_name', 'student__lastname')


admin.site.register(News)
admin.site.register(Part)
admin.site.register(UserProfile)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(Memo, MemoAdmin)
