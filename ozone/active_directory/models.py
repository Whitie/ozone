# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class ADCache(models.Model):
    username = models.CharField(_(u'Username'), max_length=100)
    expires = models.DateTimeField(_(u'Expires'), blank=True, null=True)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.username, self.expires.strftime('%c'))

    class Meta:
        verbose_name = _(u'Active Directory Cache')
        verbose_name_plural = _(u'Active Directory Caches')
