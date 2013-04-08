# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from core.models import (PedagogicJournal, JournalEntry, JournalMedia)
from core.forms import NewJournalForm, NewEntryForm
from core.views import helper as h
from core.menu import menus


# Create your views here.

@login_required
def my_entries(req):
    entries = JournalEntry.objects.select_related().filter(created_by=req.user
        ).order_by('journal__group', '-created')
    ctx = dict(page_title=_(u'My Journal Entries'), menus=menus,
        entries=entries)
    return render(req, 'journal/myentries.html', ctx)


@login_required
def list_journals(req):
    journals = PedagogicJournal.objects.select_related().all(
        ).order_by('group__job', '-group__start_date')
    if not req.user.has_perm('core.read'):
        journals = journals.filter(instructors=req.user)
    ctx = dict(page_title=_(u'Accessible Journals'), menus=menus,
        journals=journals)
    return render(req, 'journal/list.html', ctx)


@login_required
def show_media_for_entry(req, entry_id):
    entry = JournalEntry.objects.select_related().get(id=int(entry_id))
    ctx = dict(page_title=_(u'Show Media'), menus=menus, entry=entry,
        include_media=True)
    return render(req, 'journal/show_media.html', ctx)


@login_required
def add_journal(req):
    if req.method == 'POST':
        form = NewJournalForm(req.POST)
        if form.is_valid():
            form.save()
            messages.success(req, u'Neues Tagebuch wurde angelegt.')
        else:
            messages.error(req, u'Tagebuch konnte nicht angelegt werden, '
                u'für diese Gruppe existiert bereits eins.')
    journals = PedagogicJournal.objects.all().order_by('group__job',
        '-group__start_date')
    for j in journals:
        j.userlist = [x.last_name for x in j.instructors.all()]
    form = NewJournalForm()
    ctx = dict(page_title=_(u'Add new Journal for Group'),
        menus=menus, journals=journals, form=form)
    return render(req, 'journal/add.html', ctx)


@login_required
def add_entry(req, gid):
    journals = PedagogicJournal.objects.filter(group__id=int(gid),
        instructors=req.user)
    if not journals:
        messages.error(req, u'Sie haben keine Berechtigungen dieses '
                            u'Tagebuch zu ändern.')
        return redirect('core-journals')
    journal = journals[0]
    if req.method == 'POST':
        form = NewEntryForm(req.POST)
        form.fields['student'].choices = h.get_students_for_group(
            journal.group)
        jid = int(req.POST.get('journal_id'))
        if form.is_valid():
            entry = JournalEntry.objects.create(created_by=req.user,
                journal=PedagogicJournal.objects.get(id=jid),
                **form.cleaned_data)
            entry.save()
            for name, f in req.FILES.items():
                media = JournalMedia.objects.create(entry=entry, media=f)
                media.save()
            messages.success(req, u'Neuer Eintrag wurde gespeichert.')
            return redirect('core-add-entry', jid)
        else:
            messages.error(req, u'Bitte füllen Sie die Pflichtfelder aus.')
    else:
        form = NewEntryForm()
        form.fields['student'].choices = h.get_students_for_group(
            journal.group)
    ctx = dict(page_title=_(u'Add Entry'), menus=menus, form=form,
        journal=journal)
    return render(req, 'journal/add_entry.html', ctx)


@login_required
def edit_rights(req, jid):
    journals = PedagogicJournal.objects.filter(id=int(jid),
        instructors=req.user)
    if not journals:
        messages.error(req, u'Sie haben keine Berechtigungen dieses '
                            u'Tagebuch zu ändern.')
        return redirect('core-journals')
    journal = journals[0]
    if req.method == 'POST':
        added = []
        removed = []
        to_add = [int(x) for x in req.POST.getlist('add')]
        to_remove = [int(x) for x in req.POST.getlist('remove')]
        if to_add:
            for id_ in to_add:
                u = User.objects.get(id=id_)
                journal.instructors.add(u)
                added.append(unicode(u.get_profile()))
            journal.save()
            messages.success(req, u'%s hinzugefügt.' % u', '.join(added))
        if to_remove:
            for id_ in to_remove:
                u = User.objects.get(id=id_)
                journal.instructors.remove(u)
                removed.append(unicode(u.get_profile()))
            journal.save()
            messages.success(req, u'%s entfernt.' % u', '.join(removed))
        return redirect('core-journal-rights', journal.id)
    users = User.objects.exclude(username='admin').exclude(
        id__in=[x.id for x in journal.instructors.all()])
    ctx = dict(page_title=_(u'Edit Rights'), menus=menus, users=users,
        journal=journal)
    return render(req, 'journal/rights.html', ctx)
