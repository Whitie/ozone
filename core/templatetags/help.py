# -*- coding: utf-8 -*-

from django import template
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
                'id': help_slug}), 'width': 500, 'opener_class': u'.opener'}
