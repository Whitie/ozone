# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20190226_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='chemman',
            field=models.BooleanField(default=False, verbose_name='GIFTBUCH'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=8, blank=True, null=True, verbose_name='Unser Preis'),
            preserve_default=True,
        ),
    ]
