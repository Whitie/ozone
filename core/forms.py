# -*- coding: utf-8 -*-

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from core.models import News, StudentGroup, RATING_CHOICES, UserProfile
from core.html5_widgets import SearchInput5, IntegerField5


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


class CompanyRatingForm(forms.Form):
    good_quality = IntegerField5(label=_(u'Good Quality'), min_value=0,
        max_value=4, step=1)
    delivery_time = IntegerField5(label=_(u'Delivery Time'), min_value=0,
        max_value=4, step=1)
    quality = IntegerField5(label=_(u'Quality'), min_value=0, max_value=4,
        step=1)
    price = IntegerField5(label=_(u'Price'), min_value=0, max_value=4, step=1)
    service = IntegerField5(label=_(u'Service'), min_value=0, max_value=4,
        step=1)
    attainability = IntegerField5(label=_(u'Attainability'), min_value=0,
        max_value=4, step=1)
    documentation = IntegerField5(label=_(u'Documentation'), min_value=0,
        max_value=4, step=1)
    rating = forms.ChoiceField(label=_(u'Rating'), choices=RATING_CHOICES)
    note = forms.CharField(label=_(u'Note'), widget=forms.Textarea,
        required=False, help_text=_(u'This field is required if you rate '
        u'with "B".'))
