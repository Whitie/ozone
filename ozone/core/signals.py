# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from core.models import UserProfile


def create_profile(sender, **kw):
    if not 'instance' in kw or not kw.get('created', False):
        return
    instance = kw['instance']
    profile = UserProfile()
    profile.user = instance
    profile.save()

post_save.connect(create_profile, sender=User)

