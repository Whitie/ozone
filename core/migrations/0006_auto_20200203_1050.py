# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_course'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ['date'], 'verbose_name': 'Note', 'verbose_name_plural': 'Notes'},
        ),
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
            preserve_default=True,
        ),
    ]
