# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


class Menu(object):

    def __init__(self, title, *entries):
        self.title = title
        self.entries = entries

    def __iter__(self):
        for named_url, name in self.entries:
            yield named_url, name


core_menu = Menu(_(u'Core'),
    ('core-companies', _(u'Companies')),
    ('core-students', _(u'Students')),
    ('core-groups', _(u'Groups')),
)

news_menu = Menu(_(u'News'),
    ('core-add-news', _(u'Write News')),
)

menus = [core_menu, news_menu]

