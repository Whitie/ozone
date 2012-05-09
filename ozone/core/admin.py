# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from core.utils import named
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
                    'qm_rating', 'student_count')
    list_display_links = ('name', 'short_name')
    list_editable = ('phone', 'fax')
    list_filter = ('qm_rating',)
    ordering = ('name',)
    save_on_top = True
    search_fields = ('name', 'short_name', 'zip_code')

    @named(_(u'Student(s)'))
    def student_count(self, obj):
        return obj.students.filter(finished=False).count()


class StudentAdmin(admin.ModelAdmin):
    list_display = ('lastname', 'firstname', 'group', 'company', 'birthdate',
                    'phone', 'email', 'finished')
    list_display_links = ('lastname',)
    list_editable = ('phone', 'email', 'finished')
    list_filter = ('group', 'company', 'finished')
    save_on_top = True
    search_fields = ('lastname', 'company__name', 'group__job_short',
                     'barcode')


class StudentInline(admin.StackedInline):
    model = Student
    max_num = 20
    extra = 3


class StudentGroupAdmin(admin.ModelAdmin):
    inlines = (StudentInline,)
    list_display = ('__unicode__', 'job', 'start_date')
    list_display_links = ('__unicode__', 'job')
    list_filter = ('job',)
    save_on_top = True
    search_fields = ('job', 'job_short')


class MemoAdmin(admin.ModelAdmin):
    list_display = ('created_by', '__unicode__')
    list_display_links = ('created_by',)
    search_fields = ('created_by__last_name', 'student__lastname')


class NewsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'author', 'public')
    list_display_links = ('__unicode__',)
    list_editable = ('public',)
    list_filter = ('author', 'date', 'public')
    search_fields = ('title', 'text')
    ordering = ('-date',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'show_email', 'phone', 'mobile', 'part',
                    'can_login')
    list_display_links = ('__unicode__',)
    list_editable = ('phone', 'mobile', 'can_login')
    list_filter = ('part', 'can_login')
    search_fields = ('user__username', 'user__last_name', 'user__email',
                     'barcode')
    save_on_top = True

    @named(_(u'Email'))
    def show_email(self, obj):
        return obj.user.email


admin.site.register(News, NewsAdmin)
admin.site.register(Part)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(Memo, MemoAdmin)
admin.site.register(Note)
