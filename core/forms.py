# -*- coding: utf-8 -*-

from django import forms
from django.forms.widgets import CheckboxSelectMultiple, TextInput, Textarea
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from core.models import (News, RATING_CHOICES, UserProfile, PedagogicJournal,
    Student, StudentGroup, SEX_CHOICES, SUIT_CHOICES, EDU_CHOICES, Company,
    CooperationContract, AccidentEntry)
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
            for x in User.objects.filter(is_active=True).exclude(
                username='admin').order_by('last_name'))


def get_groups():
    g = [(0, u'----')] + [(x.id, x.name()) for x in StudentGroup.objects.all()
        if not x.finished()]
    return g


def get_student(sid):
    return Student.objects.get(id=int(sid))


def get_group(gid):
    try:
        return StudentGroup.objects.get(id=int(gid))
    except StudentGroup.DoesNotExist:
        return None


def get_companies():
    c = [(0, u'----')] + [(x.id, unicode(x)) for x in Company.objects.all(
        ).exclude(short_name=u'Alle').order_by('name')]
    return c


def get_company(cid):
    try:
        return Company.objects.get(id=int(cid))
    except Company.DoesNotExist:
        return None


def get_contracts():
    c = [(0, _(u'>- Select company first -<'))] + [(x.id, unicode(x)) for x
        in CooperationContract.objects.filter(active=True)]
    return c


def get_contract(cid):
    try:
        return CooperationContract.objects.get(id=int(cid))
    except CooperationContract.DoesNotExist:
        return None


def get_points():
    return [(x, unicode(x)) for x in range(101)]


def get_search_field(name):
    lookups = SEARCHES.get(name, None)
    if lookups is None:
        return ''
    else:
        return lookups[1]


class NewJournalForm(forms.ModelForm):
    class Meta:
        model = PedagogicJournal


class AccidentForm(forms.ModelForm):
    class Meta:
        model = AccidentEntry
        exclude = ('added', 'added_by')


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('author', 'date')
        widgets = {
            'title': TextInput(attrs={'class': 'input-xxlarge'}),
            'text': Textarea(attrs={'class': 'input-xxlarge'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('part', 'subjects', 'can_login', 'external', 'barcode',
                   '_barcode', '_config')


class SearchForm(forms.Form):
    search = forms.CharField(label=_(u'Search'), max_length=50,
        widget=SearchInput5(attrs={'class': 'span2'}))


class StudentSearchForm(SearchForm):
    group = forms.TypedChoiceField(coerce=int, empty_value=0, required=False)


class ExtendedSearchForm(forms.Form):
    search_for_1 = forms.TypedChoiceField(coerce=get_search_field,
        choices=SEARCHES_CHOICES,
        widget=forms.Select(attrs={'class': 'span2'}))
    search_1 = forms.CharField(max_length=50,
        widget=SearchInput5(attrs={'class': 'span2'}))
    connect_with = forms.ChoiceField(choices=(
        ('and', _(u'and')), ('or', _(u'or'))),
        widget=forms.Select(attrs={'class': 'span1'}))
    search_for_2 = forms.TypedChoiceField(coerce=get_search_field,
        choices=[('', '-----')] + SEARCHES_CHOICES, empty_value='',
        required=False, widget=forms.Select(attrs={'class': 'span2'}))
    search_2 = forms.CharField(max_length=50, required=False,
        widget=SearchInput5(attrs={'class': 'span2'}))


class NoteForm(forms.Form):
    subject = forms.CharField(label=_(u'Subject'), max_length=50)
    text = forms.CharField(label=_(u'Text'), widget=forms.Textarea)


RATINGS = (
    (0, '0 - sehr schlecht'),
    (1, '1 - schlecht'),
    (2, '2 - befriedigend'),
    (3, '3 - gut'),
    (4, '4 - sehr gut')
)


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
        choices=[], coerce=int)
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


# Forms for add student wizard

class StudentPersonalDataForm(forms.Form):
    lastname = forms.CharField(label=_(u'Lastname'), max_length=50)
    firstname = forms.CharField(label=_(u'Firstname'), max_length=50)
    sex = forms.ChoiceField(label=_(u'Sex'), choices=SEX_CHOICES)
    birthdate = forms.DateField(label=_(u'Birthdate'),
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y', '%d.%m.%y'])
    street = forms.CharField(label=_(u'Street'), max_length=100,
        required=False)
    zip_code = forms.CharField(label=_(u'Zip Code'), max_length=15,
        required=False)
    city = forms.CharField(label=_(u'City'), max_length=100, required=False)
    country = forms.CharField(label=_(u'Country'), max_length=50,
        required=False)
    phone = forms.CharField(label=_(u'Phone'), max_length=30, required=False)
    mobile = forms.CharField(label=_(u'Mobile'), required=False)
    email = forms.EmailField(label=_(u'Email'), required=False)
    emergency = forms.CharField(label=_(u'Notice in emergency'),
        max_length=100, required=False)


class StudentJobForm(forms.Form):
    group = forms.TypedChoiceField(label=_(u'Group'), choices=get_groups(),
        coerce=get_group, required=False)
    company = forms.TypedChoiceField(label=_(u'Company'),
        choices=get_companies(), coerce=get_company, required=False)
    contract = forms.TypedChoiceField(label=_(u'Cooperation Contract'),
        choices=get_contracts(), required=False, coerce=get_contract)
    cabinet = forms.CharField(label=_(u'Cabinet'), max_length=20,
        required=False)
    key = forms.CharField(label=_(u'Key'), max_length=20, required=False)
    picture = forms.ImageField(label=_(u'Picture'), required=False)


class StudentApplyForm(forms.Form):
    school_education = forms.TypedChoiceField(label=_(u'School Education'),
        choices=EDU_CHOICES, required=False, coerce=int)
    applied_to = forms.CharField(label=_(u'Applied to'), max_length=150,
        required=False)
    forwarded_to = forms.CharField(label=_(u'Forwarded to'), max_length=150,
        required=False)
    jobs = forms.CharField(label=_(u'Jobs'), max_length=150, required=False)
    test_result = forms.TypedChoiceField(label=_(u'Test Result'),
        choices=get_points(), required=False, coerce=int)
    test_date = forms.DateField(label=_(u'Test Date'), required=False,
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y', '%d.%m.%y'])
    suit_phrase = forms.TypedChoiceField(label=_(u'Suit phrase'),
        choices=SUIT_CHOICES, required=False, coerce=int)


# End of wizard


class StudentEditForm(forms.Form):
    cabinet = forms.CharField(label=_(u'Cabinet'), max_length=20,
        required=False)
    key = forms.CharField(label=_(u'Key'), max_length=20, required=False)
    exam_1 = forms.TypedChoiceField(label=_(u'Exam 1'), required=False,
        choices=get_points(), coerce=int)
    exam_2 = forms.TypedChoiceField(label=_(u'Exam 2'), required=False,
        choices=get_points(), coerce=int)
    finished = forms.BooleanField(label=_(u'Finished'), required=False)
