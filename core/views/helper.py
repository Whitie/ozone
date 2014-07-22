# -*- coding: utf-8 -*-

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.conf import settings

import core.utils.special_days_ger as sdg

from core.models import StudentGroup, PresenceDay, Student


def get_presence_day(day, student):
    """Get one presence day for one student. If day do not exist it will
    be created.

    :parameters:
        day : date
            Date (day) to get the PresenceDay object for.
        student : Student
            Student object to get the presence day for.

    :returns: PresenceDay object
    """
    pday, created = PresenceDay.objects.get_or_create(student=student,
        date=day)
    if created:
        if sdg.is_special_day(day):
            pday.entry = u'FT'
            pday.instructor = User.objects.get(username='admin')
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
    past = end < date.today() - timedelta(days=7)
    for s in students:
        tmp = []
        for i in range(dt.days + 1):
            d = start + timedelta(days=i)
            if d.weekday() not in (5, 6):
                day = get_presence_day(d, s)
                if day is not None:
                    tmp.append(day)
        if past and not any([x.entry for x in tmp]):
            for d in tmp:
                d.entry = u'/'
                d.instructor = User.objects.get(username='admin')
                d.save()
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


def get_presence_details(student):
    """Get a detailed overview from presence days for one student. Saves
    them on the student object.

    :parameters:
        student : Student
            The student to work on.

    :returns: The same student object with the following new attributes
              (all prefixed with p_)::
                  p_all: All saved presence days (entry != '')
                  p_all_days: All absent days (T, F, K, |)
                  p_all_days_percent: p_all_days in percent from p_all
                  p_ill: All illness days (K)
                  p_ill_percent: p_ill in percent from p_all
                  p_not_excused: All not excused absent days (|)
                  p_lateness_count: Count of all latenesses
                  p_latenesses: Dates of the latenesses
                  p_lateness_sum: Sum of all latenesses in minutes
    """
    q = student.presence_days.exclude(entry=u'')
    student.p_all = q.count()
    student.p_all_days = q.filter(entry__in=[u'T', u'F', u'K', u'|']).count()
    try:
        student.p_all_days_percent = (float(student.p_all_days) / student.p_all
            ) * 100
    except ZeroDivisionError:
        student.p_all_days_percent = 0.0
    student.p_ill = q.filter(entry=u'K').count()
    try:
        student.p_ill_percent = (float(student.p_ill) / student.p_all
            ) * 100
    except ZeroDivisionError:
        student.p_ill_percent = 0.0
    student.p_not_excused = q.filter(entry=u'|').count()
    student.p_holiday = q.filter(entry=u'U').count()
    student.p_lateness_count = 0
    student.p_latenesses = []
    student.p_lateness_sum = 0
    for d in q.filter(lateness__gt=0).order_by('date'):
        student.p_lateness_sum += d.lateness
        student.p_lateness_count += 1
        student.p_latenesses.append(d.date.strftime(
            settings.DEFAULT_DATE_FORMAT))
    return student


def get_studentgroups():
    return [(0, u'Alle Gruppen')] + [(x.id, x.name()) for x in
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
    profile = user.userprofile
    c = profile.config()
    s = c.get('pstudents', [])
    return Student.objects.select_related().filter(id__in=s)
