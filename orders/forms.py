# -*- coding: utf-8 -*-

from datetime import date

from django import forms
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _

from core import html5_widgets as _wid


DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y']


def get_user(uid):
    try:
        user = User.objects.get(id=int(uid))
    except User.DoesNotExist:
        user = AnonymousUser()
    return user


class OrderDayForm(forms.Form):
    day = forms.DateField(label=_(u'Next Orderday'), input_formats=DATE_FORMATS,
        help_text=_(u'Use this format: dd.mm.yyyy'))
    user = forms.TypedChoiceField(label=_(u'Responsible User'),
        coerce=get_user, empty_value=AnonymousUser())


class OrderOldForm(forms.Form):
    article_name = forms.CharField(label=_('Article'), max_length=100)
    article_id = forms.IntegerField(widget=forms.HiddenInput)


class OrderForm(forms.Form):
    count = _wid.IntegerField5(label=_(u'Count'))
    art_name = forms.CharField(label=_(u'Article'), max_length=100)
    art_supplier = forms.ChoiceField(label=_(u'Supplier'))
    art_id = forms.CharField(label=_(u'Identifier'), max_length=50,
        required=False)
    art_q = forms.CharField(label=_(u'Quantity'), max_length=20)
    art_price = forms.DecimalField(label=_(u'Price'), required=False)
    memo = forms.CharField(label=_(u'Memo'), widget=forms.Textarea(),
        required=False)
    oday = forms.ChoiceField(label=_(u'Order Day'))
    exam = forms.BooleanField(label=_(u'Exam'), required=False)
    repair = forms.BooleanField(label=_(u'Repair'), required=False)


class ShortSupplierForm(forms.Form):
    name = forms.CharField(label=_(u'Name'), max_length=100)
    customer_number = forms.CharField(label=_(u'Customer Number'),
        max_length=50, required=False)
    phone = forms.CharField(label=_(u'Phone'), max_length=30, required=False)
    fax = forms.CharField(label=_(u'Fax'), max_length=30, required=False)
    email = forms.EmailField(label=_(u'Email'), required=False)
