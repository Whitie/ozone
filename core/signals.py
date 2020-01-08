# -*- coding: utf-8 -*-

import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models.signals import post_save

from core.models import UserProfile, Student
from barcode.codex import Code39
from barcode.writer import ImageWriter


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub(r'[^\w\s-]', '', value).strip().lower())
    return re.sub(r'[-\s]+', '-', value)


def create_barcode(prefix, ident, name):
    _name = u'{0}-{1:05d}-{2}'.format(prefix, ident, name)
    _name = slugify(_name).upper()
    bc = Code39(_name, writer=ImageWriter(), add_checksum=False)
    out = StringIO()
    bc.write(out)
    return _name, out.getvalue()


def create_student_barcode(sender, **kw):
    if 'instance' not in kw or not kw.get('created', False):
        return
    instance = kw['instance']
    bc, im = create_barcode(u'STU-{0}'.format(instance.lastname[0]),
                            instance.id, instance.lastname)
    instance.barcode = bc
    content = ContentFile(im)
    instance._barcode.save('{0}.png'.format(bc), content)
    instance.save()


def create_profile(sender, **kw):
    if 'instance' not in kw or not kw.get('created', False):
        return
    instance = kw['instance']
    profile = UserProfile()
    profile.user = instance
    bc, im = create_barcode(u'USER-{0}'.format(instance.username[0]),
                            instance.id, instance.username)
    profile.barcode = bc
    content = ContentFile(im)
    profile._barcode.save('{0}.png'.format(bc), content)
    profile.save()


post_save.connect(create_profile, sender=User)
post_save.connect(create_student_barcode, sender=Student)
