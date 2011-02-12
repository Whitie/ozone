# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse


register = template.Library()


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
