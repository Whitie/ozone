# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse

from cryptography.fernet import Fernet, InvalidToken


def external_auth(req):
    if not settings.EXT_LOGIN:
        data = dict(success=False, message='External login deactivated.')
        return JsonResponse(data)
    token = req.GET.get('token', '').strip()
    if isinstance(token, unicode):
        token = token.encode('utf-8')
    fernet = Fernet(settings.EXT_LOGIN_KEY)
    try:
        s = fernet.decrypt(token, ttl=5)
    except InvalidToken:
        data = dict(success=False, message='Token manipulated or to old.')
        return JsonResponse(data)
    s = s.decode('utf-8')
    username, password = s.split(settings.MESSAGE_SEPARATOR)
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            data = dict(success=True, id=user.id, email=user.email,
                        first_name=user.first_name, last_name=user.last_name)
        else:
            data = dict(success=False, message='User is not active.')
    else:
        data = dict(success=False, message='Username and/or password wrong.')
    return JsonResponse(data)
