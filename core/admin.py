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


class CooperationContractInline(admin.StackedInline):
    model = CooperationContract
    max_num = 5
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    inlines = (ContactInline, CooperationContractInline)
    list_display = ('name', 'short_name', 'phone', 'fax', 'customer_number',
                    'student_count')
    list_display_links = ('name', 'short_name')
    list_editable = ('phone', 'fax')
    list_filter = ('cooperations__full', 'cooperations__job')
    ordering = ('name',)
    save_on_top = True
    search_fields = ('name', 'short_name', 'zip_code')

    @named(_(u'Student(s)'))
    def student_count(self, obj):
        return obj.students.filter(finished=False).count()


class CooperationContractAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'full')
    list_display_links = ('__unicode__',)
    list_editable = ('full',)
    list_filter = ('company__name', 'date', 'full')
    save_on_top = True
    ordering = ('company__name', 'date')
    search_fields = ('company__name', 'date')


class CompanyRatingAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('company', 'user', 'rating', 'rated')
    list_display_links = ('company',)
    list_filter = ('company__name', 'user', 'rating', 'rated')
    ordering = ('company__name', '-rated', 'rating')
    search_fields = ('company__name', 'user')

    def save_model(self, req, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = req.user
        obj.save()


class StudentAdmin(admin.ModelAdmin):
    list_display = ('lastname', 'firstname', 'group', 'company', 'birthdate',
                    'phone', 'email', 'finished')
    list_display_links = ('lastname',)
    list_editable = ('phone', 'email', 'finished')
    list_filter = ('group', 'company', 'finished', 'group__school_nr')
    save_on_top = True
    search_fields = ('lastname', 'company__name', 'group__job_short',
                     'barcode', 'group__school_nr')


class StudentInline(admin.StackedInline):
    model = Student
    max_num = 20
    extra = 3


class StudentGroupAdmin(admin.ModelAdmin):
    inlines = (StudentInline,)
    list_display = ('__unicode__', 'job', 'start_date', 'school_nr')
    list_display_links = ('__unicode__', 'job')
    list_filter = ('job', 'school_nr')
    list_editable = ('school_nr',)
    save_on_top = True
    search_fields = ('job', 'job_short', 'school_nr')


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
                    'subjects', 'can_login')
    list_display_links = ('__unicode__',)
    list_editable = ('phone', 'mobile', 'subjects', 'can_login')
    list_filter = ('part', 'can_login')
    search_fields = ('user__username', 'user__last_name', 'user__email',
                     'barcode', 'subjects')
    save_on_top = True

    @named(_(u'Email'))
    def show_email(self, obj):
        return obj.user.email


admin.site.register(News, NewsAdmin)
admin.site.register(Part)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CooperationContract, CooperationContractAdmin)
admin.site.register(CompanyRating, CompanyRatingAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(Memo, MemoAdmin)
admin.site.register(Note)
