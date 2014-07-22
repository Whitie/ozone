# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from decimal import Decimal
import audit_log.models.fields
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('ident', models.CharField(help_text='Article number', max_length=50, verbose_name='Identifier', blank=True)),
                ('barcode', models.CharField(help_text='Achtung, Strichcode \xfcber Scanner immer als Letztes eingeben.', max_length=40, verbose_name='Barcode', blank=True)),
                ('quantity', models.CharField(max_length=20, verbose_name='Quantity', blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=8, blank=True, null=True, verbose_name='Price')),
                ('tox_control', models.BooleanField(default=True, verbose_name='Von Toxolution kontrolliert')),
                ('supplier', models.ForeignKey(verbose_name='Supplier', blank=True, to='core.Company', null=True)),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('ident', models.PositiveIntegerField(serialize=False, verbose_name='Identifier', primary_key=True)),
                ('short_name', models.CharField(max_length=10, verbose_name='Short Name')),
                ('name', models.CharField(max_length=50, verbose_name='Name', blank=True)),
            ],
            options={
                'verbose_name': 'Cost',
                'verbose_name_plural': 'Costs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CostOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percent', models.PositiveIntegerField(verbose_name='Percent', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('cost', models.ForeignKey(verbose_name='Cost', to='orders.Cost')),
            ],
            options={
                'ordering': [b'order'],
                'verbose_name': 'Cost Order Relation',
                'verbose_name_plural': 'Cost Order Relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeliveredOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField(verbose_name='Count')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Date')),
                ('exported', models.BooleanField(default=False, verbose_name='Nach Toxolution exportiert')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': [b'order', b'-date'],
                'verbose_name': 'Delivered Order',
                'verbose_name_plural': 'Delivered Orders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField(verbose_name='Count')),
                ('memo', models.TextField(verbose_name='Memo', blank=True)),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='Added')),
                ('for_test', models.BooleanField(default=False, verbose_name='For Exam')),
                ('for_repair', models.BooleanField(default=False, verbose_name='For Repair')),
                ('state', models.CharField(default='new', max_length=10, verbose_name='State', choices=[('new', 'Neu'), ('accepted', 'Akzeptiert'), ('rejected', 'Zur\xfcckgewiesen'), ('ordered', 'Bestellt'), ('delivered', 'Geliefert')])),
                ('ordered', models.DateField(null=True, verbose_name='Ordered', blank=True)),
                ('article', models.ForeignKey(verbose_name='Article', to='orders.Article')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'permissions': ((b'can_order', 'Can make orders'), (b'extra_order', 'Can order without order day'), (b'can_change_orderstate', 'Can change the state of orders'), (b'controlling', 'View statistics for orders')),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deliveredorder',
            name='order',
            field=models.ForeignKey(verbose_name='Order', to='orders.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='costorder',
            name='order',
            field=models.ForeignKey(verbose_name='Order', to='orders.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='costs',
            field=models.ManyToManyField(to='orders.Cost', verbose_name='Costs', through='orders.CostOrder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Users'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='OrderAuditLogEntry',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('count', models.PositiveIntegerField(verbose_name='Count')),
                ('memo', models.TextField(verbose_name='Memo', blank=True)),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='Added')),
                ('for_test', models.BooleanField(default=False, verbose_name='For Exam')),
                ('for_repair', models.BooleanField(default=False, verbose_name='For Repair')),
                ('state', models.CharField(default='new', max_length=10, verbose_name='State', choices=[('new', 'Neu'), ('accepted', 'Akzeptiert'), ('rejected', 'Zur\xfcckgewiesen'), ('ordered', 'Bestellt'), ('delivered', 'Geliefert')])),
                ('ordered', models.DateField(null=True, verbose_name='Ordered', blank=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, editable=False, choices=[(b'I', 'Created'), (b'U', 'Changed'), (b'D', 'Deleted')])),
                ('action_user', audit_log.models.fields.LastUserField(editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('article', models.ForeignKey(verbose_name='Article', to='orders.Article')),
            ],
            options={
                'ordering': (b'-action_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(unique=True, verbose_name='Day', validators=[django.core.validators.MinValueValidator(datetime.date(2014, 7, 19))])),
                ('user', models.ForeignKey(verbose_name='Responsible User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Order Day',
                'verbose_name_plural': 'Order Days',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='orderauditlogentry',
            name='order_day',
            field=models.ForeignKey(verbose_name='Order Day', to='orders.OrderDay'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='order_day',
            field=models.ForeignKey(verbose_name='Order Day', to='orders.OrderDay'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Printout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal', models.BooleanField(default=True, help_text='Internal means with costs and prices.', verbose_name='Internal')),
                ('pdf', models.FileField(upload_to=b'orders/%Y/%m', verbose_name='PDF-File')),
                ('company_name', models.CharField(max_length=100, verbose_name='Company Name', blank=True)),
                ('generated', models.DateTimeField(auto_now=True, verbose_name='Generated')),
                ('order_day', models.ForeignKey(verbose_name='Order Day', to='orders.OrderDay')),
            ],
            options={
                'ordering': [b'company_name', b'-generated'],
                'verbose_name': 'Printout',
                'verbose_name_plural': 'Printouts',
            },
            bases=(models.Model,),
        ),
    ]
