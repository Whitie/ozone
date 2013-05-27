# -*- coding: utf-8 -*-

from datetime import date, timedelta

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from core.models import StudentGroup, PresenceDay, Student


def get_presence_day(day, student, in_past):
    """Get one presence day for one student. If day is in the future it will
    be created. If day is in the past and don't exists the return value is
    None.

    :parameters:
        day : date
            Date (day) to get the PresenceDay object for.
        student : Student
            Student object to get the presence day for.
        in_past : bool
            Indicates if day is in the past.

    :returns: PresenceDay object or None
    """
    if in_past:
        try:
            pday = PresenceDay.objects.get(student=student, date=day)
            return pday
        except PresenceDay.DoesNotExist:
            return
    else:
        pday, created = PresenceDay.objects.get_or_create(student=student,
            date=day)
        if created:
            pday.save()
        return pday


def get_presence(students, start, end):
    """Get all presence days for a list of students in a time period.

    :parameters:
        students : list
            List of Student objects.
        start : date
            Start date for the list.
        end : date
            End date for the list.

    :returns: List of 2-tuples with the student as first element and a list
              of all found presence days as the second element.
    """
    l = []
    dt = end - start
    past = end < date.today()
    for s in students:
        tmp = []
        for i in range(dt.days + 1):
            d = start + timedelta(days=i)
            if d.weekday() not in (5, 6):
                day = get_presence_day(d, s, past)
                if day is not None:
                    tmp.append(day)
        if not past:
            l.append((s, tmp))
        else:
            if tmp and any([x.entry for x in tmp]):
                l.append((s, tmp))
    return l


def sort_students_for_presence(students):
    """Sort students in a group by their cooperation contracts.

    :parameters:
        students : QuerySet
            Queryset of students from one group.

    :returns: List of the given Student objects sorted by full coop,
              partly coop and undefined coop.
    """
    no_contract = []
    full = []
    partly = []
    for s in students.filter(finished=False).order_by('company__short_name',
                                                      'lastname'):
        if s.contract is not None:
            if s.contract.full:
                full.append(s)
            else:
                partly.append(s)
        else:
            no_contract.append(s)
    return full + partly + no_contract


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


def get_students(user):
    profile = user.get_profile()
    c = profile.config()
    s = c.get('pstudents', [])
    return Student.objects.select_related().filter(id__in=s)
