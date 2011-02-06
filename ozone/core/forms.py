# -*- coding: utf-8 -*-

from django.forms import ModelForm

from core.models import News


class NewsForm(ModelForm):
    class Meta:
        model = News
        exclude = ('author', 'date')


