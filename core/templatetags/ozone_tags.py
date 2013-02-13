# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from core.models import InternalHelp


register = template.Library()


@register.inclusion_tag('internal_help_dlg.html', takes_context=True)
def show_help(context, help_slug):
    lang = context.get('LANGUAGE_CODE', 'en-en')
    try:
        ihelp = InternalHelp.objects.values().get(lang__istartswith=lang,
            ident=help_slug)
        return ihelp
    except InternalHelp.DoesNotExist:
        return {'title': _(u'Error'), 'text': _(u'<p>No help found for lang '
            u'%(lang)s and identifier %(id)s.</p>' % {'lang': lang,
                'ident': help_slug}), 'width': 500, 'opener_class': u'.opener'}


@register.filter(name='enumerate')
def simple_enumerate(value, start=1):
    """Usage in template code: {% for i, obj in items|enumerate %}
       or with start parameter: {% for i, obj in items|enumerate:15 %}.
       The start parameter can also be a variable.
    """
    return enumerate(value, start=start)


# Deprecated since Ozone 3.0, will be removed in 3.1
@register.tag(name='reverse')
def do_reverse_url(parser, token):
    try:
        tag, url_var = token.split_contents()
    except ValueError:
        raise (template.TemplateSyntaxError,
               'reverse tag requires exactly one argument')
    return ReverseResolver(url_var)


class ReverseResolver(template.Node):
    def __init__(self, url_var):
        self.url_var = template.Variable(url_var)

    def render(self, context):
        try:
            url_name = self.url_var.resolve(context)
            return reverse(url_name)
        except template.VariableDoesNotExist:
            return ''
