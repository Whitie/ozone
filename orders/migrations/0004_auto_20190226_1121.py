# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20170915_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderday',
            name='day',
            field=models.DateField(unique=True, verbose_name='Day', validators=[django.core.validators.MinValueValidator(datetime.date(2019, 2, 26))]),
            preserve_default=True,
        ),
    ]
