# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import audit_log.models.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderday',
            options={'verbose_name': 'Order Day', 'verbose_name_plural': 'Order Days', 'permissions': (('can_accept_odays', 'Kann Bestelltage freigeben'),)},
        ),
        migrations.AddField(
            model_name='orderday',
            name='accepted',
            field=models.BooleanField(default=True, verbose_name='Genehmigt'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deliveredorder',
            name='order',
            field=models.ForeignKey(related_name='deliveries', verbose_name='Order', to='orders.Order'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='order_day',
            field=models.ForeignKey(related_name='orders', verbose_name='Order Day', to='orders.OrderDay'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderauditlogentry',
            name='action_user',
            field=audit_log.models.fields.LastUserField(related_name='_order_audit_log_entry', editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderauditlogentry',
            name='order_day',
            field=models.ForeignKey(related_name='_auditlog_orders', verbose_name='Order Day', to='orders.OrderDay'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderday',
            name='day',
            field=models.DateField(unique=True, verbose_name='Day', validators=[django.core.validators.MinValueValidator(datetime.date(2015, 7, 10))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='printout',
            name='order_day',
            field=models.ForeignKey(related_name='printouts', verbose_name='Order Day', to='orders.OrderDay'),
            preserve_default=True,
        ),
    ]
