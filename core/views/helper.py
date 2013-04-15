# -*- coding: utf-8 -*-

from datetime import date, timedelta

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from core.models import StudentGroup, PresenceDay, Student


def get_presence(students, start, end, pdf=False):
    l = []
    dt = end - start
    past = end < date.today()
    print past
    for s in students:
        tmp = []
        for i in range(dt.days + 1):
            d = start + timedelta(days=i)
            if d.weekday() not in (5, 6):
                if not past:
                    day, created = PresenceDay.objects.get_or_create(student=s,
                        date=d)
                    if created:
                        day.save()
                    tmp.append(day)
                else:
                    try:
                        day = PresenceDay.objects.get(student=s, date=d)
                        tmp.append(day)
                    except PresenceDay.DoesNotExist:
                        pass
        if not past:
            l.append((s, tmp))
        else:
            if tmp and any([x.entry for x in tmp]):
                l.append((s, tmp))
    if pdf:
        return [x[0] for x in tmp]
    else:
        return l


def get_studentgroups():
    return [(0, _(u'All Groups'))] + [(x.id, x.name()) for x in
                                      StudentGroup.objects.all()]


def get_students_for_group(group):
    return [(0, u'------')] + [(x.id, u'%s, %s' % (x.lastname, x.firstname))
        for x in Student.objects.filter(finished=False, group=group)]


def replace_umlauts(s):
    repl = [(u'ä', u'ae'), (u'ö', u'oe'), (u'ü', u'ue'), (u'ß', u'ss')]
    s = s.lower()
    for old, new in repl:
        s = s.replace(old, new)
    return s


def make_username(last, first):
    if first:
        uname = u'{0}{1}'.format(last[:2], first[0])
    else:
        uname = last[:3]
    uname = replace_umlauts(uname)
    try:
        User.objects.get(username=uname)
    except User.DoesNotExist:
        return uname
    i = 1
    while True:
        tmp = u'{0}{1}'.format(uname, i)
        try:
            User.objects.get(username=tmp)
        except User.DoesNotExist:
            return tmp
        i += 1
