# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from django.conf import settings
from django.db.models import Q
from django.contrib import messages

from core.utils import json_rpc, remove_old_sessions
from core.models import PresenceDay, JournalEntry, Student, Company


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
def get_contracts(req, data=None):
    company = Company.objects.select_related().get(id=data['cid'])
    contracts = [{'id': x.id, 'text': unicode(x)} for x in
        company.cooperations.all()]
    return dict(res=contracts)


@json_rpc
def clean_sessions(req, data=None):
    session_count = remove_old_sessions()
    return dict(msg=u'Es wurden %d alte Sitzungen gelöscht.' % session_count)


@json_rpc
def clean_presence(req, data=None):
    today = date.today()
    day = date(today.year, today.month, 1) - timedelta(days=1)
    query = Q(entry__isnull=True) | Q(entry__exact=u'')
    q = PresenceDay.objects.filter(query, date__lt=day)
    count = q.count()
    q.delete()
    return dict(msg=u'Es wurden %d Anwesenheitstage gelöscht.' % count)


@json_rpc
def migrate30(req, data=None):
    what = data['what']
    if what == u'presence':
        q = PresenceDay.objects.filter(entry=u'*')
        c = q.count()
        for d in q:
            d.entry = u'A'
            d.save()
        return dict(msg=u'{0} Datensätze wurden geändert.'.format(c))
    return dict(msg=u'Falscher Befehl.')


@json_rpc
def delete_student(req, data):
    sid = data['student_id']
    if req.user.has_perm('core.delete_student'):
        try:
            s = Student.objects.get(id=sid)
            name = u'{0}, {1}'.format(s.lastname, s.firstname)
            pdays = s.presence_days.all()
            c = pdays.count()
            pdays.delete()
            s.journal_entries.all().delete()
            s.delete()
            messages.success(req, u'Azubi {name} und {pdays} '
                u'Anwesenheitstage wurden gelöscht!'.format(name=name,
                    pdays=c))
        except Exception as e:
            messages.error(req,
                u'Beim Löschen ist ein Fehler aufgetreten: {0}'.format(e))
    else:
        messages.error(req, u'Unzureichende Berechtigungen!')
    return dict()
