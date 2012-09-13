# -*- coding: utf-8 -*-

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from core.utils import json_rpc
from core.models import PresenceDay


@json_rpc
def update_presence(req, data):
    translation.activate(req.LANGUAGE_CODE)
    pday = PresenceDay.objects.select_for_update().get(id=data['day_id'])
    msg = [u'{0}, {1} ({2}):'.format(pday.student.lastname,
        pday.student.firstname, pday.date.strftime('%d.%m.'))]
    updated = False
    if data['presence'] != pday.entry:
        updated = True
        if data['presence']:
            pday.entry = data['presence']
            msg.append(_(u'Presence updated with %(entry)s (%(disp)s).' %
                {'entry': pday.entry, 'disp': pday.get_entry_display()}))
        else:
            pday.entry = u''
            msg.append(_(u'Presence set to unknown!'))
    if data['lateness'] != pday.lateness:
        updated = True
        if data['lateness'] is None and pday.lateness != 0:
            msg.append(_(u'Lateness %d minutes deleted!' % pday.lateness))
            pday.lateness = 0
        elif data['lateness'] is not None:
            pday.lateness = data['lateness']
            msg.append(_(u'Lateness set to %d minutes.' % pday.lateness))
    if updated:
        pday.instructor = req.user
        pday.save()
    else:
        msg.append(_(u'Nothing changed.'))
    return {'msg': u' '.join([unicode(x) for x in msg])}


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
