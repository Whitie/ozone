# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


USER_CHOICES = [(x.id, x.get_full_name() or x.username) for x in
                User.objects.all() if x.has_perm('orders.add_orderday')]
DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y']

class OrderDayForm(forms.Form):
    day = forms.DateField(label=_(u'Next Order Day'),
                          input_formats=DATE_FORMATS)
    user = forms.ChoiceField(label=_(u'Responsible User'), choices=USER_CHOICES,
                             help_text=_(u'Use this format: dd.mm.yyyy'))
