# -*- coding: utf-8 -*-

import codecs
import csv
import cStringIO
import json
import os
import re
import traceback

from datetime import date, datetime

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render as django_render
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.models import Session


GERMAN_MONTH = {
    1: u'Januar',
    2: u'Februar',
    3: u'März',
    4: u'April',
    5: u'Mai',
    6: u'Juni',
    7: u'Juli',
    8: u'August',
    9: u'September',
    10: u'Oktober',
    11: u'November',
    12: u'Dezember'
}

# Taken from werkzeug <http://werkzeug.pocoo.org>
_filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                         'LPT2', 'LPT3', 'PRN', 'NUL')


def secure_filename(filename):
    r"""Pass it a filename and it will return a secure version of it. This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`. The filename returned is an ASCII only string
    for maximum portability.

    On windows system the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename. It's your responsibility
    to ensure that the filename is unique and that you generate random
    filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    if isinstance(filename, unicode):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('ascii', 'ignore')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(
                   filename.split()))).strip('._')

    # on nt a couple of special files are present in each folder. We
    # have to ensure that the target file is not such a filename. In
    # this case we prepend an underline
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename

# End of werkzeug code #######################################################


def get_birthday_color(birthdate, day):
    bd = date(2000, *birthdate)
    td = date(2000, *day)
    if bd < td:
        return u'muted'
    elif bd == td:
        return u'text-warning'
    else:
        return u'text-success'


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
        response = func(req, *args, **kw)
        _json = json.dumps(response)
        return HttpResponse(_json, content_type='application/json')
    return wrap


def json_rpc(func):
    def wrap(req, *args, **kwargs):
        if req.method == 'POST' and '_JSON_' in req.POST:
            try:
                json_data = json.loads(req.POST['_JSON_'])
                response = func(req, json_data, *args, **kwargs)
            except Exception as e:
                print e
        else:
            response = func(req, *args, **kwargs)
        _json = json.dumps(response)
        return HttpResponse(_json, content_type='application/json')
    return wrap


def error(req, msg=''):
    if not msg:
        msg = u'Ein interner Serverfehler ist aufgetreten!'
    ctx = dict(page_title=u'Ozone Fehler', msg=msg)
    return render(req, 'error.html', ctx)


def internal_server_error(req):
    d = datetime.now()
    msg = u'%s:\n\n%s' % (d.strftime('%c'), traceback.format_exc())
    send_mail(u'Ozone Serverfehler', msg, 'dms@bbz-chemie.de',
        ['weimann@bbz-chemie.de', 'weimann.th@gmail.com'])
    ctx = dict(page_title=u'Ozone Fehler')
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


def remove_old_sessions():
    q = Session.objects.filter(expire_date__lt=datetime.now())
    count = q.count()
    q.delete()
    return count


def get_date(value, default=None):
    if value is None:
        return default
    else:
        try:
            d = datetime.strptime(value, '%d.%m.%Y').date()
            return d
        except ValueError:
            return default


class UnicodeCSVWriter(object):

    def __init__(self, fp, fieldnames, dialect=csv.excel, encoding='utf-8',
                 **kw):
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames=fieldnames,
                                     dialect=dialect, **kw)
        self.stream = fp
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeheader(self):
        self.writerow(row=None)

    def writerow(self, row):
        if row is None:
            self.writer.writeheader()
        else:
            encoded = {k: v.encode('utf-8') for k, v in row.iteritems()}
            self.writer.writerow(encoded)
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
