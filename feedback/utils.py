# -*- coding: utf-8 -*-

import random
import uuid


TOKEN_CHARS = '0123456789abcdefghijklmnopqrstuvwxyz'
TOKEN_LENGTH = 5


def make_unique_token(s):
    text = u'{0}-{1}'.format(s, uuid.uuid4())
    base = len(TOKEN_CHARS)
    num = 0
    for c in text:
        num += ord(c)
    res = []
    while num:
        num, rem = divmod(num, base)
        res.append(TOKEN_CHARS[rem])
    while len(res) < TOKEN_LENGTH:
        res.append(random.choice(TOKEN_CHARS))
    return ''.join(res)
