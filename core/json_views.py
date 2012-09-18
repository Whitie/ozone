# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from core.utils import json_rpc
from core.models import PresenceDay


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
