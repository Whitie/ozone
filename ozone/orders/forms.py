# -*- coding: utf-8 -*-

from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from orders.models import Article, OrderDay
from core.models import Company
from core import html5_widgets as _wid


USER_CHOICES = [(x.id, x.get_full_name() or x.username) for x in
                User.objects.all() if x.has_perm('orders.can_order')]
DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y']
ODAY_CHOICES = [(x.id, unicode(x)) for x in OrderDay.objects.filter(
                day__gt=date.today()).order_by('-day')]
ARTICLE_CHOICES = [(x.id, unicode(x)) for x in Article.objects.all().order_by(
                    'name', '-quantity')]
SUPPLIER_CHOICES = [(x.id, x.name) for x in Company.objects.all()]


class OrderDayForm(forms.Form):
    day = forms.DateField(label=_(u'Next Order Day'),
        input_formats=DATE_FORMATS, widget=_wid.DateInput5(),
        help_text=_(u'Use this format: dd.mm.yyyy'))
    user = forms.ChoiceField(label=_(u'Responsible User'), choices=USER_CHOICES)


class OrderOldForm(forms.Form):
    article = forms.ChoiceField(label=_('Article'), choices=ARTICLE_CHOICES)


class OrderForm(forms.Form):
    count = _wid.IntegerField5(label=_('Count'))
    art_name = forms.CharField(label=_('Article'), max_length=100)
    art_supplier = forms.ChoiceField(label=_('Supplier'),
        choices=SUPPLIER_CHOICES)
    art_id = forms.CharField(label=_('Identifier'), max_length=50,
        required=False)
    art_q = forms.CharField(label=_('Quantity'), max_length=20)
    art_price = forms.DecimalField(label=_('Price'), required=False)
    memo = forms.CharField(label=_('Memo'), widget=forms.Textarea(),
        required=False)
    oday = forms.ChoiceField(label=_('Order Day'), choices=ODAY_CHOICES)
    exam = forms.BooleanField(label=_('For Exam'), required=False)
    repair = forms.BooleanField(label=_('Repair'), required=False)
