# -*- coding: utf-8 -*-

from datetime import datetime, date

from django.utils import simplejson
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def named(verbose_name):
    def decorate(f):
        f.short_description = verbose_name
        return f
    return decorate


def json_view(func):
    def wrap(req, *args, **kw):
        response = func(req, *args, **kw)
        json = simplejson.dumps(response)
        return HttpResponse(json, mimetype='application/json')
    return wrap


def error(req, msg=''):
    if not msg:
        msg = _('An internal server error occured.')
    ctx = dict(page_title=_('Ozone Error'), msg=msg)
    return render_to_response('error.html', ctx,
        context_instance=RequestContext(req))


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
