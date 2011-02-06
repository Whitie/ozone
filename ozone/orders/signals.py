# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db.models.signals import pre_save
from orders.models import Cost

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None


_PATH = os.path.dirname(os.path.abspath(__file__))


def text2image(text, filename):
    font = ImageFont.truetype(os.path.join(_PATH, 'DejaVuSansMono.ttf'), 12)
    size = font.getsize(text)
    im = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), text, font=font, fill='black')
    im = im.rotate(90)
    if os.path.isfile(filename):
        os.remove(filename)
    im.save(filename)


def create_image(sender, **kw):
    if Image is None or not 'instance' in kw:
        return
    instance = kw['instance']
    name = unicode(instance)
    filename = u'{0}.png'.format(name.replace(' ', ''))
    path = os.path.join(settings.MEDIA_ROOT, 'labels', filename)
    text2image(name, path)
    instance._label = u'labels/{0}'.format(filename)

pre_save.connect(create_image, sender=Cost)

