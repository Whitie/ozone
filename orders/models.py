# -*- coding: utf-8 -*-

from datetime import date
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from audit_log.models.managers import AuditLog
from core.models import Company


class OrderDay(models.Model):
    day = models.DateField(_(u'Day'), unique=True,
                           validators=[MinValueValidator(date.today())])
    user = models.ForeignKey(User, verbose_name=_(u'Responsible User'))
    accepted = models.BooleanField(u'Genehmigt', default=True)

    def __unicode__(self):
        return self.day.strftime('%d.%m.%Y (%W)')

    def has_accepted_order(self):
        for o in self.orders.all():
            if o.state in (u'accepted', u'ordered'):
                return True
        return False

    class Meta:
        verbose_name = _(u'Order Day')
        verbose_name_plural = _(u'Order Days')
        permissions = (
            ('can_accept_odays', u'Kann Bestelltage freigeben'),
        )


class Article(models.Model):
    TAX_CHOICES = (
        (7, u'7%'),
        (19, u'19%'),
    )
    name = models.CharField(_(u'Name'), max_length=100)
    supplier = models.ForeignKey(Company, verbose_name=_(u'Supplier'),
                                 blank=True, null=True)
    ident = models.CharField(_(u'Identifier'), max_length=50,
                             help_text=_(u'Article number'), blank=True)
    barcode = models.CharField(
        _(u'Barcode'), max_length=40, blank=True,
        help_text=(u'Achtung, Strichcode über Scanner immer als Letztes '
                   u'eingeben.')
    )
    quantity = models.CharField(_(u'Quantity'), max_length=20, blank=True)
    price = models.DecimalField(u'Nettopreis', max_digits=8, decimal_places=2,
                                blank=True, null=True, default=Decimal())
    discount_price = models.DecimalField(
        _(u'Unser Preis (netto)'), max_digits=8, decimal_places=2,
        blank=True, null=True, default=Decimal()
    )
    tax = models.PositiveSmallIntegerField(
        u'MWST', choices=TAX_CHOICES, default=19
    )
    tox_control = models.BooleanField(u'Von Toxolution kontrolliert',
                                      default=True)
    chemman = models.BooleanField(_('GIFTBUCH'), default=False)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.short_desc())

    def get_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    def fullprice(self):
        if self.discount_price:
            price = self.discount_price
            discount = u' (R)'
        else:
            price = self.price
            discount = u''
        return u'{0:.2f} {1}{2}'.format(price, settings.CURRENCY[1], discount)

    def price_with_tax(self):
        return self.get_price() * (1 + self.tax/Decimal(100))

    def short_desc(self):
        if self.discount_price:
            price = u' {0}/{1:.2f}{2} (R)'.format(
                self.quantity, self.discount_price, settings.CURRENCY[1]
            )
        else:
            if self.price:
                price = u' {0}/{1:.2f}{2}'.format(self.quantity, self.price,
                                                  settings.CURRENCY[1])
            else:
                price = u''
        return u'{0}{1}'.format(self.supplier, price)

    class Meta:
        verbose_name = _(u'Article')
        verbose_name_plural = _(u'Articles')


class Cost(models.Model):
    ident = models.PositiveIntegerField(_(u'Identifier'), primary_key=True)
    short_name = models.CharField(_(u'Short Name'), max_length=10)
    name = models.CharField(_(u'Name'), max_length=50, blank=True)

    def __unicode__(self):
        return u'{0} {1}'.format(self.short_name, self.ident)

    class Meta:
        verbose_name = _(u'Cost')
        verbose_name_plural = _(u'Costs')


STATE_CHOICES = (
    (u'new', u'Neu'), (u'accepted', u'Akzeptiert'),
    (u'rejected', u'Zurückgewiesen'), (u'ordered', u'Bestellt'),
    (u'delivered', u'Geliefert')
)

_mapper = dict(
    new=(u'success', u'icon-plus'),
    accepted=(u'primary', u'icon-ok'),
    rejected=(u'danger', u'icon-ban-circle'),
    ordered=(u'info', u'icon-shopping-cart'),
    delivered=(u'inverse', u'icon-inbox'),
)


class Order(models.Model):
    count = models.PositiveIntegerField(_(u'Count'))
    article = models.ForeignKey(Article, verbose_name=_(u'Article'))
    costs = models.ManyToManyField(Cost, through='CostOrder',
                                   verbose_name=_(u'Costs'))
    users = models.ManyToManyField(User, verbose_name=_(u'Users'))
    memo = models.TextField(_(u'Memo'), blank=True)
    added = models.DateTimeField(_(u'Added'), auto_now_add=True)
    order_day = models.ForeignKey(OrderDay, verbose_name=_(u'Order Day'),
                                  related_name='orders')
    for_test = models.BooleanField(_(u'For Exam'), default=False)
    for_repair = models.BooleanField(_(u'For Repair'), default=False)
    state = models.CharField(_(u'State'), max_length=10, default=u'new',
                             choices=STATE_CHOICES)
    ordered = models.DateField(_(u'Ordered'), blank=True, null=True)

    audit_log = AuditLog()

    def __unicode__(self):
        names = [unicode(x.username) for x in self.users.all()]
        return u'{0}x {1} ({2})'.format(self.count, self.article.name,
                                        u', '.join(names))

    def price(self):
        """This is without tax."""
        try:
            return self.count * self.article.price
        except Exception as error:
            print error
            return 0.0

    def fullprice(self):
        return self.article.price_with_tax() * self.count

    def state_icon(self):
        return _mapper[self.state][1]

    def state_btn(self):
        return _mapper[self.state][0]

    def is_complete(self):
        delivered = sum([x.count for x in
                         self.deliveries.all()])
        return delivered >= self.count

    class Meta:
        verbose_name = _(u'Order')
        verbose_name_plural = _(u'Orders')
        permissions = (
            ('can_order', u'Can make orders'),
            ('extra_order', u'Can order without order day'),
            ('can_change_orderstate', u'Can change the state of orders'),
            ('controlling', u'View statistics for orders'),
        )


class DeliveredOrder(models.Model):
    order = models.ForeignKey(Order, verbose_name=_(u'Order'),
                              related_name='deliveries')
    count = models.PositiveIntegerField(_(u'Count'))
    date = models.DateField(_(u'Date'), auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    exported = models.BooleanField(u'Nach Toxolution exportiert',
                                   default=False)

    def __unicode__(self):
        return u'{0}x {1} {2}'.format(
            self.count, self.order.article.name,
            self.date.strftime('%Y-%m-%d')
        )

    class Meta:
        verbose_name = _(u'Delivered Order')
        verbose_name_plural = _(u'Delivered Orders')
        ordering = ['order', '-date']


class CostOrder(models.Model):
    cost = models.ForeignKey(Cost, verbose_name=_(u'Cost'))
    order = models.ForeignKey(Order, verbose_name=_(u'Order'))
    percent = models.PositiveIntegerField(
        _(u'Percent'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __unicode__(self):
        return u'{0} {1}: {2}%'.format(self.order, self.cost, self.percent)

    class Meta:
        verbose_name = _(u'Cost Order Relation')
        verbose_name_plural = _(u'Cost Order Relations')
        ordering = ['order']


class Printout(models.Model):
    order_day = models.ForeignKey(OrderDay, verbose_name=_(u'Order Day'),
                                  related_name='printouts')
    internal = models.BooleanField(
        _(u'Internal'),
        help_text=_(u'Internal means with costs and prices.'), default=True
    )
    pdf = models.FileField(_(u'PDF-File'), upload_to='orders/%Y/%m')
    company_name = models.CharField(_(u'Company Name'), max_length=100,
                                    blank=True)
    generated = models.DateTimeField(_(u'Generated'), auto_now=True)

    def __unicode__(self):
        return u'{0} ({1})'.format(unicode(self.order_day), self.company_name)

    class Meta:
        verbose_name = _(u'Printout')
        verbose_name_plural = _(u'Printouts')
        ordering = ['company_name', '-generated']
