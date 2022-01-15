# -*- coding: utf-8 -*-


def userconf(req):
    ctx = {'userprofile': None, 'userconfig': {}}
    if req.user.is_authenticated():
        p = req.user.userprofile
        ctx['userprofile'] = p
        ctx['userconfig'] = p.config()
    return ctx


def set_global_vars(req):
    from django.conf import settings
    # from core.models import Configuration
    # c = Configuration.objects.all().order_by('id').last()
    return {
        'LOGO_URL': settings.LOGO_URL,
        'CURRENCY_SYM': settings.CURRENCY[1],
        'CURRENCY_NAME': settings.CURRENCY[0],
        'VERSION': settings.VERSION,
        'LIMIT': settings.ORDER_LIMIT,
        'INTERNAL_LINKS': settings.INTERNAL_LINKS,
    }
