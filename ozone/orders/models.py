# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import Company

# Create your models here.

class OrderDay(models.Model):
    day = models.DateField(_(u'Day'), unique=True,
        validators=[MinValueValidator(datetime.now())])
    user = models.ForeignKey(User, verbose_name=_(u'Responsible User'))

    def __unicode__(self):
        return self.day.strftime('%Y-%m-%d (%W)')

    class Meta:
        verbose_name = _(u'Order Day')
        verbose_name_plural = _(u'Order Days')


class Article(models.Model):
    name = models.CharField(_(u'Name'), max_length=100)
    supplier = models.ForeignKey(Company, verbose_name=_(u'Supplier'),
        blank=True, null=True)
    ident = models.CharField(_(u'Identifier'), max_length=50,
        help_text=_(u'Article number'), blank=True)
    quantity = models.CharField(_(u'Quantity'), max_length=20, blank=True)
    price = models.DecimalField(_(u'Price'), max_digits=8, decimal_places=2,
        blank=True)

    def __unicode__(self):
        if self.price:
            price = u' {0}/{1}€'.format(self.quantity, self.price)
        else:
            price = u''
        return u'{0} ({1}{2})'.format(self.name, self.supplier, price)

    class Meta:
        verbose_name = _(u'Article')
        verbose_name_plural = _(u'Articles')


class Cost(models.Model):
    ident = models.PositiveIntegerField(_(u'Identifier'), primary_key=True)
    short_name = models.CharField(_(u'Short Name'), max_length=10)
    name = models.CharField(_(u'Name'), max_length=50, blank=True)
    _label = models.CharField(max_length=100, blank=True, editable=False)

    def __unicode__(self):
        return u'{0} {1}'.format(self.short_name, self.ident)

    @property
    def label(self):
        return '{0}{1}'.format(settings.MEDIA_URL, self._label)

    class Meta:
        verbose_name = _(u'Cost')
        verbose_name_plural = _(u'Costs')


STATE_CHOICES = ((u'new', _(u'New')), (u'accepted', _(u'Accepted')),
    (u'rejected', _(u'Rejected')), (u'ordered', _(u'Ordered')),
    (u'delivered', _(u'Delivered')))

class Order(models.Model):
    count = models.PositiveIntegerField(_(u'Count'))
    article = models.ForeignKey(Article, verbose_name=_(u'Article'))
    costs = models.ManyToManyField(Cost, through='CostOrder',
        verbose_name=_(u'Costs'))
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    memo = models.TextField(_(u'Memo'), blank=True)
    added = models.DateTimeField(_(u'Added'), auto_now_add=True)
    order_day = models.ForeignKey(OrderDay, verbose_name=_(u'Order Day'))
    for_test = models.BooleanField(_(u'For test'), default=False)
    for_repair = models.BooleanField(_(u'For Repair'), default=False)
    state = models.CharField(_(u'State'), max_length=10, default='new',
        choices=STATE_CHOICES)
    ordered = models.DateField(_(u'Ordered'), blank=True, null=True)

    def __unicode__(self):
        name = unicode(self.user.get_profile())
        return u'{0}x {1} ({2})'.format(self.count, self.article.name, name)

    def is_complete(self):
        delivered = sum([x.count for x in
                         self.deliveredorder_set.objects.all()])
        return delivered == self.count

    class Meta:
        verbose_name = _(u'Order')
        verbose_name_plural = _(u'Orders')
        permissions = (('can_print', u'Can print orders'),
                       ('can_change_state', u'Can change the state of orders'))


class DeliveredOrder(models.Model):
    order = models.ForeignKey(Order, verbose_name=_(u'Order'))
    count = models.PositiveIntegerField(_(u'Count'))
    date = models.DateField(_(u'Date'), auto_now_add=True)

    def __unicode__(self):
        return u'{0}x {1} {2}'.format(self.count,
            self.order.article.name, self.date.strftime('%Y-%m-%d'))

    class Meta:
        verbose_name = _(u'Delivered Order')
        verbose_name_plural = _(u'Delivered Orders')


class CostOrder(models.Model):
    cost = models.ForeignKey(Cost, verbose_name=_(u'Cost'))
    order = models.ForeignKey(Order, verbose_name=_(u'Order'))
    percent = models.PositiveIntegerField(_(u'Percent'),
        validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __unicode__(self):
        return u'{0} {1}: {2}%'.format(self.order, self.cost, self.percent)

