# -*- coding: utf-8 -*-


def userconf(req):
    ctx = {'_profile': None, '_config': {}}
    if req.user.is_authenticated():
        p = req.user.get_profile()
        ctx['_profile'] = p
        ctx['_config'] = p.config()
    return ctx

def set_global_vars(req):
    from django.conf import settings
    return {'LOGO_URL': settings.LOGO_URL}
