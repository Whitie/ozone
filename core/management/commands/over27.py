# -*- coding: utf-8 -*-

import codecs
import json
import os

from django.core.management.base import BaseCommand

from core.models import Student


_PATH = os.path.dirname(os.path.abspath(os.getcwd()))
_DUMP = os.path.join(_PATH, 'over27.json')


class Command(BaseCommand):
    help = u'Dump all active students to JSON.'

    def handle(self, *args, **options):
        students = Student.objects.filter(finished=False)
        res = []
        for s in students:
            try:
                bd = s.birthdate.strftime('%Y-%m-%d')
            except:
                bd = '1900-01-01'
            res.append({
                'Nachname': s.lastname,
                'Vorname': s.firstname,
                'Geburtstag': bd,
            })
        self.stdout.write('Writing to %s' % _DUMP)
        with codecs.open(_DUMP,'w', encoding='utf-8') as fp:
            json.dump(res, fp, indent=2)

