# -*- coding: utf-8 -*-

import traceback

from datetime import date, datetime

from django.core.mail import send_mail
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render as django_render
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def named(verbose_name):
    def decorate(f):
        f.short_description = verbose_name
        return f
    return decorate


def render(request, template, context=None, app=u'core'):
    ctx = context or {}
    ctx['app'] = app
    return django_render(request, template, ctx)


def json_view(func):
    def wrap(req, *args, **kw):
        cur_lang = translation.get_language()
        try:
            translation.activate(req.LANGUAGE_CODE)
            response = func(req, *args, **kw)
            json = simplejson.dumps(response)
            return HttpResponse(json, mimetype='application/json')
        finally:
            translation.activate(cur_lang)
    return wrap


def json_rpc(func):
    def wrap(req, *args, **kwargs):
        cur_lang = translation.get_language()
        try:
            translation.activate(req.LANGUAGE_CODE)
            if req.method == 'POST' and '_JSON_' in req.POST:
                json_data = simplejson.loads(req.POST['_JSON_'])
                response = func(req, json_data, *args, **kwargs)
            else:
                response = func(req, *args, **kwargs)
            json = simplejson.dumps(response)
            return HttpResponse(json, mimetype='application/json')
        finally:
            translation.activate(cur_lang)
    return wrap


def error(req, msg=''):
    if not msg:
        msg = _('An internal server error occured.')
    ctx = dict(page_title=_('Ozone Error'), msg=msg)
    return render(req, 'error.html', ctx)


def internal_server_error(req):
    d = datetime.now()
    msg = u'%s:\n\n%s' % (d.strftime('%c'), traceback.format_exc())
    send_mail(u'Ozone Serverfehler', msg, 'dms@bbz-chemie.de',
        ['weimann@bbz-chemie.de', 'weimann.th@gmail.com'])
    ctx = dict(page_title=_('Ozone Error'))
    return render(req, '500.html', ctx)


def check_for_import(module, msg=''):
    def decorate(f):
        def pdf_error(req, *args, **kwargs):
            return error(req, msg)
        if module is None:
            return pdf_error
        else:
            return f
    return decorate


def any_permission_required(perms, login_url=None, raise_exception=False):
    def check_perms(user):
        for perm in perms:
            if user.has_perm(perm):
                return True
        if raise_exception:
            raise PermissionDenied
        return False
    return user_passes_test(check_perms, login_url=login_url)


def get_edu_year(start):
    delta = date.today() - start
    days = delta.days
    if days < 365:
        return 1
    elif days < 730:
        return 2
    elif days < 1095:
        return 3
    elif days < 1460:
        return 4
    return 5
