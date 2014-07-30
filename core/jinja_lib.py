# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import get_callable, reverse, NoReverseMatch
from django.contrib.staticfiles.storage import staticfiles_storage
from pytz import timezone, utc

from jinja2 import FileSystemLoader, PackageLoader, ChoiceLoader, Environment


DEFAULT_EXTENSIONS = set([
    'jinja2.ext.do',
    'jinja2.ext.with_',
])
DEFAULT_FORMATS = {
    'DATE_FORMAT': '%Y-%m-%d',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'TIME_FORMAT': '%H:%M:%S',
}


loaders = []
for path in getattr(settings, 'TEMPLATE_DIRS', ()):
    loaders.append(FileSystemLoader(path))
for app in settings.INSTALLED_APPS:
    loaders.append(PackageLoader(app))

default_formats = DEFAULT_FORMATS.copy()
default_formats.update(getattr(settings, 'JINJA_DEFAULT_FORMATS', {}))
jinja_extensions = getattr(settings, 'JINJA_EXTENSIONS', ())
jinja_extensions = set(jinja_extensions) | DEFAULT_EXTENSIONS
env = Environment(extensions=jinja_extensions, loader=ChoiceLoader(loaders))

if 'jinja2.ext.i18n' in jinja_extensions:
    from django.utils import translation
    env.install_gettext_translations(translation)

global_imports = getattr(settings, 'JINJA_GLOBALS', ())
for imp in global_imports:
    func = get_callable(imp)
    try:
        env.globals[func.jinja_name] = func
    except AttributeError:
        env.globals[func.__name__] = func

global_filters = getattr(settings, 'JINJA_FILTERS', ())
for f in global_filters:
    func = get_callable(f)
    try:
        env.filters[func.jinja_name] = func
    except AttributeError:
        env.filters[func.__name__] = func

global_tests = getattr(settings, 'JINJA_TESTS', ())
for test in global_tests:
    func = get_callable(test)
    try:
        env.tests[func.jinja_name] = func
    except AttributeError:
        env.tests[func.__name__] = func


# Common used functions and filters
def url(view_name, *args, **kwargs):
    """Usage: {{ url("view_name", foo, "bar", baz=10) }}"""
    try:
        return reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        try:
            name = settings.SETTINGS_MODULE.split('.')[0]
            return reverse('{0}.{1}'.format(name, view_name), args=args,
                kwargs=kwargs)
        except NoReverseMatch:
            return ''


def static(path):
    """Usage: {{ static('path/to/file') }}"""
    return staticfiles_storage.url(path)


def date(obj, format_string=None):
    """Usage: {{ VAR|date() }}
              {{ VAR|date('%Y') }}

    Format string syntax is Python datetime.strftime syntax. `obj` must be a
    datetime.datetime or datetime.date object.
    """
    if obj in (None, ''):
        return ''
    tz = timezone(settings.TIME_ZONE)
    if format_string is None:
        format_string = 'DATE_FORMAT'
    fmt = default_formats.get(format_string, format_string)
    local_dt = obj.astimezone(tz)
    return local_dt.strftime(fmt)


def now():
    """Usage: {{ now() }}

    It can be combined with the date filter: {{ now()|date('%W') }} will
    return the weeknumber.
    """
    tz = timezone(settings.TIME_ZONE)
    utc_dt = datetime.now(utc)
    return utc_dt.astimezone(tz)


# Register common used functions and filters
env.globals['url'] = url
env.globals['static'] = static
env.globals['now'] = now

env.filters['date'] = date


# Render functions
def render_to_string(template, dict_=None, context_instance=None):
    dict_ = dict_ or {}
    ctx = {}
    tpl = env.get_template(template)
    if not context_instance:
        return tpl.render(**dict_)
    for d in context_instance.dicts:
        ctx.update(d)
    ctx.update(dict_)
    try:
        return tpl.render(**ctx)
    finally:
        context_instance.pop()


def render_jinja(request, template, ctx=None, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    Uses a RequestContext by default.
    """
    ctx = ctx or {}
    httpresponse_kwargs = {
        'content_type': kwargs.pop('content_type', None),
        'status': kwargs.pop('status', None),
    }

    ctx['app'] = kwargs.pop('app', 'core')

    if 'context_instance' in kwargs:
        context_instance = kwargs.pop('context_instance')
        if kwargs.get('current_app', None):
            raise ValueError('If you provide a context_instance you must '
                             'set its current_app before calling render()')
    else:
        current_app = kwargs.pop('current_app', None)
        context_instance = RequestContext(request, current_app=current_app)

    kwargs['context_instance'] = context_instance

    return HttpResponse(render_to_string(template, ctx, **kwargs),
                        **httpresponse_kwargs)
