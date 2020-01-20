# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


class Menu(object):

    def __init__(self, title, *entries):
        self.title = title
        self.entries = entries

    def __iter__(self):
        for named_url, name in self.entries:
            yield named_url, name


core_menu = Menu(
    _(u'Core'),
    ('core-companies', _(u'Companies')),
    ('core-students', _(u'Students')),
    ('core-groups', _(u'Groups')),
    ('core-colleagues', _(u'Colleagues')),
    ('core-presence', _(u'Presences')),
    ('core-accidents', _(u'Accidents')),
    ('core-students-archive', _(u'Archive')),
    ('core-presence-monthly', u'Monatsübersicht'),
)

journal_menu = Menu(
    _(u'Journals'),
    ('core-myentries', _(u'My Entries')),
    ('core-add-journal', _(u'Add new Journal')),
    ('core-journals', _(u'Manage Journals')),
)

extra_menu = Menu(
    _(u'Extra'),
    ('core-birthdays', _(u'Coming Birthdays')),
    ('core-phonelist', _(u'Internal Phonelist')),
    ('core-company-notes', u'Firmenkontakte'),
)

news_menu = Menu(
    _(u'News'),
    ('core-add-news', _(u'Write News')),
)

menus = [core_menu, journal_menu, extra_menu, news_menu]
