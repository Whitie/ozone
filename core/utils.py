# -*- coding: utf-8 -*-

from django.utils import simplejson
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _


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
