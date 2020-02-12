# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _

from core import html5_widgets as _wid
from core.models import Company


DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y']


def get_user(uid):
    try:
        user = User.objects.get(id=int(uid))
    except User.DoesNotExist:
        user = AnonymousUser()
    return user


class OrderDayForm(forms.Form):
    day = forms.DateField(
        label=_(u'Next Orderday'), input_formats=DATE_FORMATS,
        help_text=_(u'Use this format: dd.mm.yyyy')
    )
    user = forms.TypedChoiceField(
        label=_(u'Responsible User'),
        coerce=get_user, empty_value=AnonymousUser()
    )


class BaseOrderForm(forms.Form):
    count = _wid.IntegerField5(label=_(u'Count'))
    art_name = forms.CharField(label=_(u'Article'), max_length=100)
    art_supplier_name = forms.CharField(
        label=_(u'Supplier'), max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    art_supplier_id = forms.IntegerField(widget=forms.HiddenInput)
    art_id = forms.CharField(label=u'Artikelnummer', max_length=50,
                             required=False)
    art_q = forms.CharField(label=_(u'Quantity'), max_length=20)
    art_price = forms.CharField(
        label=u'Nettopreis', required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    memo = forms.CharField(label=_(u'Memo'), widget=forms.Textarea,
                           required=False)
    exam = forms.BooleanField(label=_(u'Exam'), required=False)
    repair = forms.BooleanField(label=_(u'Repair'), required=False)
    tox = forms.BooleanField(label=u'Muss in Toxolution', required=False)


class OrderForm(BaseOrderForm):
    oday = forms.ChoiceField(label=_(u'Order Day'))


class ShortSupplierForm(forms.Form):
    name = forms.CharField(label=_(u'Name'), max_length=100)
    customer_number = forms.CharField(label=_(u'Customer Number'),
                                      max_length=50, required=False)
    phone = forms.CharField(label=_(u'Phone'), max_length=30, required=False)
    fax = forms.CharField(label=_(u'Fax'), max_length=30, required=False)
    email = forms.EmailField(label=_(u'Email'), required=False)
    web = forms.URLField(label=_(u'Homepage'), required=False)


USER_CHOICES = ((x.id, x.last_name) for x in User.objects.all())


class SummarizeForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('rating', 'rating_note', 'rating_users')
