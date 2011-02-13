# -*- coding: utf-8 -*-

import os
import re

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save

from core.models import UserProfile, Student
from barcode import get_barcode
from barcode.writer import ImageWriter

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


def create_profile(sender, **kw):
    if not 'instance' in kw or not kw.get('created', False):
        return
    instance = kw['instance']
    profile = UserProfile()
    profile.user = instance
    profile.save()


def create_barcode(sender, **kw):
    print kw
    if not 'instance' in kw:
        return
    from django.conf import settings
    instance = kw['instance']
    _name = slugify(instance.lastname).upper()
    bc = u'%s-%05d-%s' % (_name[0], instance.id, _name)
    code = get_barcode('code39', bc, writer=ImageWriter())
    filename = code.save(os.path.join(settings.MEDIA_ROOT, 'barcodes', bc))
    name = os.path.splitext(os.path.split(filename)[1])[0]
    instance.barcode = name


post_save.connect(create_profile, sender=User)
pre_save.connect(create_barcode, sender=Student)
