# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


class Menu(object):

    def __init__(self, title, *entries):
        self.title = title
        self.entries = entries

    def __iter__(self):
        for url, name in self.entries:
            yield url, name


news_menu = Menu(_(u'News'),
    ('/core/add_news', _(u'Write News')),
    ('/test', u'TEST')
)

menus = [news_menu]

