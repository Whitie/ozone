# -*- coding: utf-8 -*-

import os

from hashlib import sha512
from random import randint
from time import time

from django.utils import simplejson
from django.http import HttpResponse
from django.contrib.auth import authenticate

from core.models import DesktopSession


HEADER = 'HTTP_OZONE_DESKTOP_CLIENT'
USER_ID = 'ozone_desktop_user_id'
TOKEN_ID = 'ozone_desktop_token'
LOGIN_TOKEN = 'undefined'
MAX_AGE = 8 * 60 * 60
ERROR_MSG = u'Sie konnten nicht angemeldet werden.'
SUCCESS_MSG = u'Login erfolgreich.'

_tokens = {}


def get_token(ip):
    while True:
        t = sha512(os.urandom(randint(40, 80)) + str(time()) + ip).hexdigest()
        if t not in _tokens:
            _tokens[t] = time()
            return t


def clean_token_cache():
    now = time()
    for token, ti in _tokens.items():
        if now - ti > MAX_AGE:
            del _tokens[token]


def process_desktop_request(req):
    try:
        data = simplejson.loads(req.body)
    except ValueError:
        data = {}
    token = data.get(TOKEN_ID, '')
    uid = data.get(USER_ID, 0)
    ip = req.META.get('REMOTE_ADDR', '0.0.0.0')
    if not token or token == LOGIN_TOKEN:
        user = None
    else:
        try:
            s = DesktopSession.objects.get(user__id=uid, token=token)
            s.ip = ip
            s.save()
            user = s.user
        except DesktopSession.DoesNotExist:
            user = None
    return data, user


def do_login(req):
    d = req.desktop_data
    if 'username' not in d or 'password' not in d:
        return
    u = authenticate(username=d['username'], password=d['password'])
    if u is not None:
        if u.is_active:
            p = u.get_profile()
            if p.can_login:
                ip = req.META.get('REMOTE_ADDR', '0.0.0.0')
                t = get_token(ip)
                s, created = DesktopSession.objects.get_or_create(user=u)
                s.ip = ip
                s.token = t
                s.save()
                return u


class DesktopClientMiddleware:

    def process_request(self, request):
        clean_token_cache()
        if HEADER not in request.META:
            print 'Abbruch'
            return
        data, user = process_desktop_request(request)
        request.desktop_data = data
        request.desktop_user = user
        request.do_login = False
        if user is None:
            user = do_login(request)
            if user is None:
                request.do_login = True
                return HttpResponse(simplejson.dumps({'error': ERROR_MSG}),
                     content_type='application/json')
            else:
                request.desktop_user = user
                d = {'success': SUCCESS_MSG, USER_ID: user.id,
                    TOKEN_ID: user.desktop_session.token}
                return HttpResponse(simplejson.dumps(d),
                    content_type='application/json')

    def process_response(self, request, response):
        if HEADER not in request.META or request.do_login:
            return response
        c = simplejson.loads(response.content)
        c[USER_ID] = request.desktop_user.id
        s = request.desktop_user.desktop_session
        s.token = get_token(request.META.get('REMOTE_ADDR', '0.0.0.0'))
        s.save()
        c[TOKEN_ID] = s.token
        response.content = simplejson.dumps(c)
        return response
