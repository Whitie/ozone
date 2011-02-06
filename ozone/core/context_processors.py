# -*- coding: utf-8 -*-


def userconf(req):
    ctx = {'_profile': None, '_config': {}}
    if req.user.is_authenticated():
        p = req.user.get_profile()
        ctx['_profile'] = p
        ctx['_config'] = p.config()
    return ctx
