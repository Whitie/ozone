# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200108_1328'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Name')),
                ('job', models.CharField(max_length=10, verbose_name='Beruf (K\xfcrzel)', blank=True)),
            ],
            options={
                'ordering': ['job', 'name'],
                'verbose_name': 'Kurs',
                'verbose_name_plural': 'Kurse',
            },
            bases=(models.Model,),
        ),
    ]
