# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import News, StudentGroup
from core.html5_widgets import SearchInput5


GROUP_CHOICES = ([(0, _(u'All Groups'))] +
    [(x.id, x.name()) for x in StudentGroup.objects.all()])


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('author', 'date')


class SearchForm(forms.Form):
    search = forms.CharField(label=_(u'Search'), max_length=50,
        widget=SearchInput5())


class StudentSearchForm(SearchForm):
    group = forms.TypedChoiceField(choices=GROUP_CHOICES, coerce=int,
        empty_value=0, required=False)


class NoteForm(forms.Form):
    subject = forms.CharField(label=_(u'Subject'), max_length=50)
    text = forms.CharField(label=_(u'Text'), widget=forms.Textarea)
