# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20200212_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderday',
            name='day',
            field=models.DateField(unique=True, verbose_name='Day', validators=[django.core.validators.MinValueValidator(datetime.date(2020, 2, 13))]),
            preserve_default=True,
        ),
    ]
