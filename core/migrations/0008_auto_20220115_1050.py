# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200203_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='start_date',
            field=models.DateField(default=None, null=True, verbose_name='Ausbildungsbeginn', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentauditlogentry',
            name='start_date',
            field=models.DateField(default=None, null=True, verbose_name='Ausbildungsbeginn', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='presenceday',
            name='entry',
            field=models.CharField(default=b'', max_length=2, verbose_name='Entry', blank=True, choices=[('', 'leer'), ('A', 'anwesend'), ('AC', 'getestet anwesend'), ('W', 'WebEx / Lehrbrief'), ('T', 'nur telefonisch entschuldigt'), ('|', 'fehlt unentschuldigt'), ('K', 'krank (Nachweis vorhanden)'), ('FT', 'Feiertag'), ('B', 'Berufsschule anwesend'), ('BK', 'keine Berufsschulkarte vorgelegt'), ('BE', 'Berufsschule entschuldigt'), ('F', 'Freistellung'), ('Pr', 'Pr\xfcfung'), ('U', 'Urlaub'), ('O', 'OSZ (Kurs)'), ('/', 'nicht im bbz'), ('P', 'Praktikum'), ('BU', 'Bildungsurlaub'), ('*F', 'anwesend freigestellt')]),
            preserve_default=True,
        ),
    ]
