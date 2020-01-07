# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20190226_1129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderauditlogentry',
            options={'ordering': ('-action_date',), 'default_permissions': ()},
        ),
        migrations.AlterField(
            model_name='orderday',
            name='day',
            field=models.DateField(unique=True, verbose_name='Day', validators=[django.core.validators.MinValueValidator(datetime.date(2020, 1, 7))]),
        ),
    ]
