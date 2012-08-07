# -*- coding: utf-8 -*-


def userconf(req):
    ctx = {'userprofile': None, 'userconfig': {}}
    if req.user.is_authenticated():
        p = req.user.get_profile()
        ctx['userprofile'] = p
        ctx['userconfig'] = p.config()
    return ctx


def set_global_vars(req):
    from django.conf import settings
    return {'LOGO_URL': settings.LOGO_URL}
