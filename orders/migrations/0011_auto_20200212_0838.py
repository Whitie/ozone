# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_auto_20200203_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='tax',
            field=models.PositiveSmallIntegerField(default=19, verbose_name='MWST', choices=[(7, '7%'), (19, '19%')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=8, blank=True, null=True, verbose_name='Unser Preis (netto)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=8, blank=True, null=True, verbose_name='Nettopreis'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderday',
            name='day',
            field=models.DateField(unique=True, verbose_name='Day', validators=[django.core.validators.MinValueValidator(datetime.date(2020, 2, 12))]),
            preserve_default=True,
        ),
    ]
