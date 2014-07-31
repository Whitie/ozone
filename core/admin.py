# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from core.utils import named
from core.models import *


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'phone', 'fax', 'pdflatex')
    list_display_links = ('name',)
    list_editable = ('short_name', 'phone', 'fax', 'pdflatex')


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
                    'student_count', 'rate')
    list_display_links = ('name', 'short_name')
    list_editable = ('phone', 'fax', 'customer_number', 'rate')
    list_filter = ('cooperations__full', 'cooperations__job', 'rate')
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
    list_display = ('lastname', 'firstname', 'group', 'company',
                    'birthdate', 'phone', 'email', 'finished')
    list_display_links = ('lastname',)
    list_editable = ('phone', 'email', 'finished')
    list_filter = ('group', 'company', 'finished')
    save_on_top = True
    search_fields = ('lastname', 'company__name', 'group__job_short',
                     'barcode', 'group__school_nr')


class StudentInline(admin.StackedInline):
    model = Student
    max_num = 20
    extra = 3


class StudentGroupAdmin(admin.ModelAdmin):
    inlines = (StudentInline,)
    list_display = ('__unicode__', 'job', 'start_date', 'school_nr',
                    'student_count')
    list_display_links = ('__unicode__', 'job')
    list_filter = ('job', 'school_nr')
    list_editable = ('school_nr',)
    save_on_top = True
    search_fields = ('job', 'job_short', 'school_nr')

    @named(_(u'Student(s)'))
    def student_count(self, obj):
        return obj.students.filter(finished=False).count()


class MemoAdmin(admin.ModelAdmin):
    list_display = ('student', 'text', 'created_by', 'created')
    list_display_links = ('student',)
    list_filter = ('student__group', 'created_by', 'created')
    search_fields = ('created_by__last_name', 'student__lastname')
    ordering = ('-created', 'student__group')
    exclude = ('created_by',)

    def save_model(self, req, obj, form, change):
        obj.created_by = req.user
        obj.save()


class NoteAdmin(admin.ModelAdmin):
    list_display = ('get_contact', 'subject', 'text', 'user', 'date')
    list_display_links = ('get_contact',)
    list_filter = ('user', 'date')
    search_fields = ('user__last_name', 'contact__lastname',
                     'contact__company__name', 'subject')
    exclude = ('user',)

    def get_contact(self, obj):
        return u'%s (%s)' % (obj.contact, obj.contact.company.short_name)

    def save_model(self, req, obj, form, change):
        obj.user = req.user
        obj.save()


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
    list_filter = ('part', 'external', 'can_login')
    search_fields = ('user__username', 'user__last_name', 'user__email',
                     'barcode', 'subjects')
    save_on_top = True

    @named(_(u'Email'))
    def show_email(self, obj):
        return obj.user.email


class PresenceDayAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'entry', 'lateness', 'excused', 'note',
                    'instructor')
    list_display_links = ('student',)
    list_editable = ('entry', 'lateness', 'excused', 'note')
    list_filter = ('student', 'student__group', 'date', 'instructor')
    search_fields = ('student__lastname', 'date')
    ordering = ('-date', 'student__lastname')
    save_on_top = True

    def save_model(self, req, obj, form, change):
        if getattr(obj, 'instructor', None) is None:
            obj.instructor = req.user
        obj.save()


class PresencePrintoutAdmin(admin.ModelAdmin):
    list_display = ('company', 'group', 'date', 'generated')
    list_display_links = ('company',)
    list_filter = ('company', 'group', 'date')
    search_fields = ('company__name', 'company__short_name', 'group__job',
                     'group__job_short')
    ordering = ('date', 'company__name', 'group__job')


class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_users', 'description')
    list_display_links = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

    @named(_(u'User'))
    def get_users(self, obj):
        users = [unicode(x) for x in obj.profiles.all()]
        return u', '.join(users)


class PedagogicJournalAdmin(admin.ModelAdmin):
    list_display = ('group', 'get_users', 'created')
    list_display_links = ('group',)
    list_filter = ('group',)
    search_fields = ('group__job', 'group__job_short')

    @named(_(u'Instructors'))
    def get_users(self, obj):
        users = [unicode(x.userprofile()) for x in obj.instructors.all()]
        return u', '.join(users)


class JournalMediaInline(admin.TabularInline):
    model = JournalMedia
    max_num = 3
    extra = 1


class JournalEntryAdmin(admin.ModelAdmin):
    inlines = [JournalMediaInline]
    list_display = ('journal', 'student', 'get_short_entry', 'created',
                    'edited', 'created_by')
    list_display_links = ('journal',)
    list_filter = ('journal', 'student', 'created_by', 'created')
    search_fields = ('student__lastname', 'created_by__last_name')

    def save_model(self, req, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = req.user
        obj.save()

    @named(_(u'Last Edit'))
    def edited(self, obj):
        if obj.created == obj.last_edit:
            return u'-'
        else:
            return obj.last_edit.strftime(settings.DEFAULT_DATETIME_FORMAT)


class JournalMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'media')
    list_display_links = ('id',)
    list_filter = ('entry',)


class AccidentEntryAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'get_injured', 'place', 'violation',
        'notify')
    list_display_links = ('date_time',)
    list_editable = ('notify', 'violation')
    list_filter = ('date_time', 'place', 'violation', 'notify')
    search_fields = ('student__lastname', 'employee__last_name', 'witness',
        'helper', 'violation', 'violation_def')
    ordering = ('-date_time', 'place__name')

    @named(_(u'Injured'))
    def get_injured(self, obj):
        return unicode(obj.injured)

    def save_model(self, req, obj, form, change):
        if getattr(obj, 'added_by', None) is None:
            obj.added_by = req.user
        obj.save()


admin.site.register(News, NewsAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CooperationContract, CooperationContractAdmin)
admin.site.register(CompanyRating, CompanyRatingAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(PresenceDay, PresenceDayAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(PresencePrintout, PresencePrintoutAdmin)
admin.site.register(PDFPrintout)
admin.site.register(PedagogicJournal, PedagogicJournalAdmin)
admin.site.register(JournalEntry, JournalEntryAdmin)
admin.site.register(JournalMedia, JournalMediaAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(InternalHelp)
admin.site.register(Place)
admin.site.register(AccidentEntry, AccidentEntryAdmin)
