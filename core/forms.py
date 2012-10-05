# -*- coding: utf-8 -*-

from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from core.models import (News, RATING_CHOICES, UserProfile, PedagogicJournal,
    Student)
from core.html5_widgets import SearchInput5


DAYS = ((_(u'Mon'), _(u'Mon')), (_(u'Tue'), _(u'Tue')), (_(u'Wed'), _(u'Wed')),
    (_(u'Thu'), _(u'Thu')), (_(u'Fri'), _(u'Fri')))


def get_user():
    return ((x.id, unicode(x.get_profile())) for x in
            User.objects.exclude(username='admin'))


def get_student(sid):
    return Student.objects.get(id=int(sid))


class NewJournalForm(forms.ModelForm):
    class Meta:
        model = PedagogicJournal


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('author', 'date')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('part', 'subjects', 'can_login', 'external', 'barcode',
                   '_barcode', '_config')


class SearchForm(forms.Form):
    search = forms.CharField(label=_(u'Search'), max_length=50,
        widget=SearchInput5())


class StudentSearchForm(SearchForm):
    group = forms.TypedChoiceField(coerce=int, empty_value=0, required=False)


class NoteForm(forms.Form):
    subject = forms.CharField(label=_(u'Subject'), max_length=50)
    text = forms.CharField(label=_(u'Text'), widget=forms.Textarea)


RATINGS = ((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'))


class CompanyRatingForm(forms.Form):
    good_quality = forms.TypedChoiceField(label=_(u'Good Quality'),
        coerce=int, choices=RATINGS)
    delivery_time = forms.TypedChoiceField(label=_(u'Delivery Time'),
        coerce=int, choices=RATINGS)
    quality = forms.TypedChoiceField(label=_(u'Quality'),
        coerce=int, choices=RATINGS)
    price = forms.TypedChoiceField(label=_(u'Price'),
        coerce=int, choices=RATINGS)
    service = forms.TypedChoiceField(label=_(u'Service'),
        coerce=int, choices=RATINGS)
    attainability = forms.TypedChoiceField(label=_(u'Attainability'),
        coerce=int, choices=RATINGS)
    documentation = forms.TypedChoiceField(label=_(u'Documentation'),
        coerce=int, choices=RATINGS)
    rating = forms.ChoiceField(label=_(u'Rating'), choices=RATING_CHOICES)
    note = forms.CharField(label=_(u'Note'), widget=forms.Textarea,
        required=False, help_text=_(u'This field is required if you rate '
        u'with "B".'))


class PresenceForm(forms.Form):
    instructor = forms.TypedChoiceField(label=_(u'Instructor'),
        choices=get_user(), coerce=int)
    course = forms.CharField(label=_(u'Course'), max_length=50, required=False)
    school_days = forms.MultipleChoiceField(label=_(u'School days'),
        choices=DAYS, required=False, widget=CheckboxSelectMultiple)


class NewEntryForm(forms.Form):
    student = forms.TypedChoiceField(label=_(u'Student'), coerce=get_student)
    event = forms.CharField(label=_(u'Event'), max_length=50, required=False)
    text = forms.CharField(label=_(u'Text'), widget=forms.Textarea)

