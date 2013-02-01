# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.sessions.models import Session
from django.db.models import Q

from core.utils import json_rpc
from core.models import PresenceDay, JournalEntry, Student


@json_rpc
def update_presence(req, data):
    pday = PresenceDay.objects.select_for_update().get(id=data['day_id'])
    msg = [u'{0}, {1} ({2}):'.format(pday.student.lastname,
        pday.student.firstname, pday.date.strftime('%d.%m.'))]
    updated = False
    if data['presence'] != pday.entry:
        updated = True
        if data['presence']:
            pday.entry = data['presence']
            msg.append(u'Anwesenheit aktualisiert mit %(entry)s (%(disp)s).' %
                {'entry': pday.entry, 'disp': pday.get_entry_display()})
        else:
            pday.entry = u''
            msg.append(u'Anwesenheit auf unbekannt gesetzt!')
    if data['lateness'] != pday.lateness:
        updated = True
        if data['lateness'] is None and pday.lateness != 0:
            msg.append(u'Verspätung %d Minuten gelöscht!' % pday.lateness)
            pday.lateness = 0
        elif data['lateness'] is not None:
            pday.lateness = data['lateness']
            msg.append(u'Verspätung auf %d Minuten gesetzt.' % pday.lateness)
    if updated:
        pday.instructor = req.user
        pday.save()
    else:
        msg.append(u'Nichts verändert.')
    return {'msg': u' '.join(msg)}


@json_rpc
def update_day(req, data):
    pday = PresenceDay.objects.select_for_update().get(id=data['day_id'])
    updated = False
    if data['entry'] != pday.entry:
        updated = True
        pday.entry = data['entry']
    if data['lateness'] != pday.lateness:
        updated = True
        if data['lateness'] is None:
            pday.lateness = 0
        else:
            pday.lateness = data['lateness']
    if data['note'] != pday.note:
        updated = True
        pday.note = data['note']
    if updated:
        if pday.instructor != req.user:
            pday.instructor = req.user
        pday.save()
    return {'instructor': unicode(pday.instructor.get_profile()),
            'updated': updated}


@json_rpc
def get_entries_for_student(req, data):
    try:
        student = Student.objects.get(id=data['student_id'])
    except Student.DoesNotExist:
        return {'has_data': False}
    entries = JournalEntry.objects.select_related().filter(
        student=student, journal__id=data['journal_id']).order_by('-created')
    tmp = []
    ret = dict(last=student.lastname, first=student.firstname)
    for e in entries:
        d = dict(inst=unicode(e.created_by.get_profile()))
        if e.event:
            d['txt'] = u'{0}: {1}'.format(e.event, e.text)
        else:
            d['txt'] = e.text
        d['created'] = e.created.strftime(settings.DEFAULT_DATETIME_FORMAT)
        tmp.append(d)
    ret['entries'] = tmp
    ret['has_data'] = bool(tmp)
    return ret


@json_rpc
def clean_sessions(req, data=None):
    q = Session.objects.filter(expire_date__lt=datetime.now())
    count = q.count()
    q.delete()
    return dict(msg=u'Es wurden %d alte Sitzungen gelöscht.' % count)


@json_rpc
def clean_presence(req, data=None):
    today = date.today()
    day = date(today.year, today.month, 1) - timedelta(days=1)
    query = Q(entry__isnull=True) | Q(entry__exact=u'')
    q = PresenceDay.objects.filter(query, date__lt=day)
    count = q.count()
    q.delete()
    return dict(msg=u'Es wurden %d Anwesenheitstage gelöscht.' % count)
