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


SEARCHES = {
    'lastname': (_(u'Lastname'), 'lastname__icontains'),
    'firstname': (_(u'Firstname'), 'firstname__icontains'),
    'email': (_(u'Email'), 'email__icontains'),
    'cabinet': (_(u'Cabinet Nr.'), 'cabinet__icontains'),
    'key': (_(u'Key Nr.'), 'key__icontains'),
    'barcode': (_(u'Barcode'), 'barcode__istartswith'),
    'company': (_(u'Company Name'), 'company__name__icontains'),
}

SEARCHES_CHOICES = sorted([(x, y[0]) for x, y in SEARCHES.iteritems()],
                          key=lambda x: x[1])


def get_user():
    return ((x.id, u'{0}, {1}'.format(x.last_name, x.first_name))
            for x in User.objects.exclude(username='admin').order_by(
            'last_name'))


def get_student(sid):
    return Student.objects.get(id=int(sid))


def get_search_field(name):
    lookups = SEARCHES.get(name, None)
    if lookups is None:
        return ''
    else:
        return lookups[1]


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


class ExtendedSearchForm(forms.Form):
    search_for_1 = forms.TypedChoiceField(coerce=get_search_field,
        choices=SEARCHES_CHOICES)
    search_1 = forms.CharField(max_length=50, widget=SearchInput5())
    connect_with = forms.ChoiceField(choices=(
        ('and', _(u'and')), ('or', _(u'or'))))
    search_for_2 = forms.TypedChoiceField(coerce=get_search_field,
        choices=[('', '-----')] + SEARCHES_CHOICES, empty_value='',
        required=False)
    search_2 = forms.CharField(max_length=50, widget=SearchInput5(),
        required=False)


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
    include_supported_days = forms.BooleanField(label=_(u'Include supported '
        u'days'), required=False)


class NewEntryForm(forms.Form):
    student = forms.TypedChoiceField(label=_(u'Student'), coerce=get_student)
    event = forms.CharField(label=_(u'Event'), max_length=50, required=False)
    text = forms.CharField(label=_(u'Text'), widget=forms.Textarea)


class NewUserForm(forms.Form):
    name_prefix = forms.CharField(label=_(u'Name Prefix'), max_length=12)
    lastname = forms.CharField(label=_(u'Lastname'), max_length=30)
    firstname = forms.CharField(label=_(u'Firstname'), max_length=30,
        required=False)
    street = forms.CharField(label=_(u'Street'), max_length=100,
        required=False)
    zip_code = forms.CharField(label=_(u'Zip Code'), max_length=15,
        required=False)
    city = forms.CharField(label=_(u'City'), max_length=100, required=False)
    country = forms.CharField(label=_(u'Country'), max_length=50,
        required=False)
    email = forms.EmailField(label=_(u'Email'), required=False)
    phone = forms.CharField(label=_(u'Phone'), max_length=30, required=False)
    mobile = forms.CharField(label=_(u'Mobile'), max_length=30, required=False)
    birthdate = forms.DateField(label=_(u'Birthdate'), required=False,
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y', '%d.%m.%y'])
    subjects = forms.CharField(label=_(u'Subjects'), max_length=150,
        required=False, widget=forms.TextInput(attrs={'size': '100'}))
    can_login = forms.BooleanField(label=_(u'Can Login'), required=False)
