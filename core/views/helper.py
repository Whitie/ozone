# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils.translation import ugettext as _

from core.models import StudentGroup, PresenceDay, Student


def get_presence(students, start, end):
    l = []
    dt = end - start
    for s in students:
        tmp = []
        for i in range(dt.days + 1):
            d = start + timedelta(days=i)
            if d.weekday() not in (5, 6):
                day, created = PresenceDay.objects.get_or_create(student=s,
                    date=d)
                if created:
                    day.save()
                tmp.append(day)
        l.append((s, tmp))
    return l


def get_studentgroups():
    return [(0, _(u'All Groups'))] + [(x.id, x.name()) for x in
                                      StudentGroup.objects.all()]


def get_students_for_group(group):
    return [(0, u'------')] + [(x.id, u'%s, %s' % (x.lastname, x.firstname))
        for x in Student.objects.filter(finished=False, group=group)]
