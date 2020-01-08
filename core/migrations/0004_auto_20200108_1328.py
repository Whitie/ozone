# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200107_1403'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contactauditlogentry',
            options={'ordering': ('-action_date',)},
        ),
        migrations.AlterModelOptions(
            name='studentauditlogentry',
            options={'ordering': ('-action_date',)},
        ),
        migrations.AddField(
            model_name='student',
            name='finished_on',
            field=models.DateField(null=True, verbose_name='Beendet am', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentauditlogentry',
            name='finished_on',
            field=models.DateField(null=True, verbose_name='Beendet am', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='email',
            field=models.EmailField(max_length=75, verbose_name='Email', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=75, verbose_name='Email', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contactauditlogentry',
            name='email',
            field=models.EmailField(max_length=75, verbose_name='Email', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(max_length=75, verbose_name='Email', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='sex',
            field=models.CharField(max_length=1, verbose_name='Sex', choices=[(b'M', 'Male'), (b'F', 'Female'), (b'X', b'divers')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='email',
            field=models.EmailField(max_length=75, verbose_name='Email', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='sex',
            field=models.CharField(max_length=1, verbose_name='Sex', choices=[(b'M', 'Male'), (b'F', 'Female'), (b'X', b'divers')]),
            preserve_default=True,
        ),
    ]
