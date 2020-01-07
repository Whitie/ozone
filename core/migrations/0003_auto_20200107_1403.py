# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20170915_0910'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contactauditlogentry',
            options={'ordering': ('-action_date',), 'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='studentauditlogentry',
            options={'ordering': ('-action_date',), 'default_permissions': ()},
        ),
        migrations.AlterField(
            model_name='company',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email', blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email', blank=True),
        ),
        migrations.AlterField(
            model_name='contactauditlogentry',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email', blank=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email', blank=True),
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email', blank=True),
        ),
    ]
