# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt

from core.utils import desktop_view


@csrf_exempt
@desktop_view
def test(req):
    return {'hello': u'world'}
