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
    ('core-presence', _(u'Presences')),
    ('core-students-archive', _(u'Archive')),
)

extra_menu = Menu(_(u'Extra'),
    ('core-birthdays', _(u'Coming Birthdays')),
)

news_menu = Menu(_(u'News'),
    ('core-index', _(u'Read News')),
    ('core-add-news', _(u'Write News')),
)

menus = [core_menu, extra_menu, news_menu]
