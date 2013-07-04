# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.utils import translation
from django.core.urlresolvers import get_callable, reverse, NoReverseMatch

from jinja2 import FileSystemLoader, PackageLoader, ChoiceLoader, Environment


loaders = []
for path in getattr(settings, 'TEMPLATE_DIRS', ()):
    loaders.append(FileSystemLoader(path))
for app in settings.INSTALLED_APPS:
    loaders.append(PackageLoader(app))

jinja_extensions = getattr(settings, 'JINJA_EXTENSIONS', ())
env = Environment(extensions=jinja_extensions, loader=ChoiceLoader(loaders))

if 'jinja2.ext.i18n' in jinja_extensions:
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
    """Usage: {% url("view_name", foo, "bar", baz=10) %}"""
    try:
        return reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        try:
            name = settings.SETTINGS_MODULE.split('.')[0]
            return reverse('{0}.{1}'.format(name, view_name), args=args,
                kwargs=kwargs)
        except NoReverseMatch:
            return ''


# Register common used functions and filters
env.globals['url'] = url


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

    ctx['app'] = kwargs.pop('app', u'core')

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
