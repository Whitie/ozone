# -*- coding: utf-8 -*-

import string

from calendar import monthrange
from datetime import datetime, date, timedelta

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from core import utils
from core.models import (News, Company, Student, StudentGroup, Contact, Note,
    CompanyRating, PresenceDay, UserProfile, PRESENCE_CHOICES)
from core.forms import (NewsForm, SearchForm, StudentSearchForm, NoteForm,
                        CompanyRatingForm, ProfileForm)
from core.menu import menus
from barcode.codex import Code39
try:
    from barcode.writer import ImageWriter
except ImportError:
    ImageWriter = None


# Helper

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


# Create your views here.

def index(req):
    if req.user.is_authenticated():
        news_list = News.objects.all()
    else:
        news_list = News.objects.filter(public=True)
    paginator = Paginator(news_list, 10)
    try:
        page = int(req.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        news = paginator.page(page)
    except (EmptyPage, InvalidPage):
        news = paginator.page(paginator.num_pages)
    ctx = dict(page_title=_(u'Ozone Home'), menus=menus, news=news)
    return render(req, 'index.html', ctx)


@login_required
def edit_profile(req):
    profile = req.user.get_profile()
    if req.method == 'POST':
        form = ProfileForm(req.POST, instance=profile)
        form.save()
        messages.success(req, _(u'All changes saved.'))
    else:
        form = ProfileForm(instance=profile)
    ctx = dict(page_title=_(u'My Profile'), menus=menus, form=form)
    return render(req, 'profile.html', ctx)


@login_required
def internal_phonelist(req):
    profiles = UserProfile.objects.select_related().filter(external=False
        ).exclude(user__username='admin').order_by('user__last_name')
    ctx = dict(page_title=_(u'Internal Phonelist'), menus=menus,
        profiles=profiles)
    return render(req, 'phonelist.html', ctx)


@permission_required('core.add_news')
def add_news(req):
    if req.method == 'POST':
        form = NewsForm(req.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = req.user
            news.save()
            messages.success(req, _(u'The News were added.'))
            return redirect('/')
        messages.error(req, _(u'Please correct the wrong fields.'))
    else:
        form = NewsForm()
    ctx = dict(page_title=_(u'Add News'), menus=menus, form=form)
    return render(req, 'news/add.html', ctx)


@permission_required('core.add_note')
def add_note(req, id):
    contact = get_object_or_404(Contact, pk=int(id))
    company = contact.company
    old_notes = contact.notes.all().order_by('-date')
    if req.method == 'POST':
        form = NoteForm(req.POST)
        if form.is_valid():
            note = Note(subject=form.cleaned_data['subject'],
                text=form.cleaned_data['text'])
            note.user = req.user
            note.contact = contact
            note.save()
            messages.success(req, _(u'New note saved.'))
            return redirect('/core/companies/addnote/{0}/'.format(id))
        else:
            messages.error(req, _(u'Please enter subject and text.'))
    else:
        form = NoteForm()
    ctx = dict(page_title=_(u'Add Note'), menus=menus, form=form,
        contact=contact, company=company, notes=old_notes)
    return render(req, 'companies/add_note.html', ctx)


def do_login(req):
    if req.method == 'POST':
        next_page = req.POST.get('next', '/')
        form = AuthenticationForm(req, req.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                p = user.get_profile()
                if user.is_active and p.can_login:
                    login(req, user)
                    messages.success(req, _(u'Login accepted.'))
                    return redirect(next_page)
                else:
                    messages.error(req, _(u'Account is disabled.'))
            else:
                messages.error(req, _(u'Username and/or password incorrect.'))
    else:
        next_page = req.GET.get('next', '/')
        form = AuthenticationForm()
        req.session.set_test_cookie()
    ctx = dict(page_title=_(u'Login Page'), form=form, next_page=next_page)
    return render(req, 'login.html', ctx)


def do_logout(req):
    logout(req)
    messages.success(req, _(u'Logged out.'))
    return redirect('/')


@login_required
def company_details(req, id):
    company = Company.objects.get(pk=int(id))
    students = company.students.select_related().filter(finished=False
        ).order_by('group__job', 'lastname')
    ctx = dict(page_title=_(u'Details: %s' % company.name), menus=menus,
        c=company, single_view=True, students=students)
    return render(req, 'companies/view_company.html', ctx)


@login_required
def list_companies(req, startchar=''):
    if req.method == 'POST':
        form = SearchForm(req.POST)
        if form.is_valid():
            s = form.cleaned_data['search']
            companies = Company.objects.select_related().filter(
                Q(name__icontains=s) | Q(short_name__icontains=s))
        else:
            companies = Company.objects.none()
            messages.error(req, _(u'Invalid search query.'))
    else:
        form = SearchForm()
        if not startchar:
            companies = Company.objects.select_related().all()
            for c in string.ascii_uppercase:
                companies = companies.exclude(name__istartswith=c)
        else:
            companies = Company.objects.select_related().filter(
                name__istartswith=startchar)
    ctx = dict(page_title=_(u'Companies'), companies=companies, menus=menus,
        startchar=startchar, chars=string.ascii_uppercase, form=form,
        single_view=False)
    return render(req, 'companies/list.html', ctx)


@login_required
def list_all_companies(req, only_with_students=False):
    q = Company.objects.select_related().all().order_by('name')
    if only_with_students:
        companie_list = [x for x in q if x.has_students()]
    else:
        companie_list = list(q)
    paginator = Paginator(companie_list, 15)
    try:
        page = int(req.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        companies = paginator.page(page)
    except (EmptyPage, InvalidPage):
        companies = paginator.page(paginator.num_pages)
    ctx = dict(page_title=_(u'All Companies'), companies=companies,
        menus=menus, only_with_students=only_with_students, single_view=False,
        page=page)
    return render(req, 'companies/list_all.html', ctx)


@login_required
def list_students(req, startchar='', archive=False):
    if req.method == 'POST':
        form = StudentSearchForm(req.POST)
        form.fields['group'].choices = get_studentgroups()
        if form.is_valid():
            s = form.cleaned_data['search']
            q = (Q(lastname__istartswith=s) | Q(company__name__icontains=s) |
                Q(barcode__istartswith=s) | Q(cabinet__icontains=s))
            if form.cleaned_data['group']:
                q &= Q(group__id=form.cleaned_data['group'])
            else:
                q |= Q(group__job_short__icontains=s)
            students = Student.objects.select_related().filter(q)
        else:
            students = Student.objects.none()
            messages.error(req, _(u'Invalid search query.'))
    else:
        form = StudentSearchForm()
        form.fields['group'].choices = get_studentgroups()
        if not startchar:
            students = Student.objects.select_related().all()
            for c in string.ascii_uppercase:
                students = students.exclude(lastname__istartswith=c)
        else:
            students = Student.objects.select_related().filter(
                lastname__istartswith=startchar)
    students = students.filter(finished=archive)
    for s in students:
        q = s.presence_days.filter(entry=u'K')
        s.ill = q.count()
        s.ex = q.filter(excused=True).count()
        s.nex = s.ill - s.ex
        s.all_days = s.presence_days.filter(entry__in=[u'T', u'F', u'K', u'|']
            ).count()
    title = _(u'Students Archive') if archive else _(u'Students')
    ctx = dict(page_title=title, students=students, menus=menus,
        archive=archive, startchar=startchar, chars=string.ascii_uppercase,
        form=form)
    return render(req, 'students/list.html', ctx)


@login_required
def list_all_students(req):
    student_list = Student.objects.select_related().all(
        ).order_by('company__name', 'lastname')
    paginator = Paginator(student_list, 30)
    try:
        page = int(req.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        students = paginator.page(page)
    except (EmptyPage, InvalidPage):
        students = paginator.page(paginator.num_pages)
    ctx = dict(page_title=_(u'List of all students'), menus=menus,
        students=students, page=page)
    return render(req, 'students/list_all.html', ctx)


@login_required
def list_groups(req):
    g = StudentGroup.objects.select_related().all()
    groups = [x for x in g if not x.finished()]
    ctx = dict(page_title=_(u'Groups'), groups=groups, menus=menus)
    return render(req, 'students/groups.html', ctx)


@login_required
def group_details(req, gid):
    try:
        gid = int(gid)
    except ValueError:
        messages.error(req, _(u'Group ID must be an integer.'))
        return redirect('core-groups')
    try:
        group = StudentGroup.objects.select_related().get(pk=gid)
    except StudentGroup.DoesNotExist:
        messages.error(req, _(u'Group with ID %d does not exist.' % gid))
        return redirect('core-groups')
    ctx = dict(page_title=_(u'Group Detail'), group=group, menus=menus)
    return render(req, 'students/group_detail.html', ctx)


@login_required
def presence_overview(req):
    jobs = StudentGroup.objects.values_list('job', flat=True)
    jobs = list(set(jobs))
    jobs.sort()
    groups = []
    for j in jobs:
        g = StudentGroup.objects.select_related().filter(job=j).order_by(
            'start_date')
        groups.append((j, g))
    ctx = dict(page_title=_(u'Group Overview'), groups=groups, menus=menus)
    return render(req, 'presence/overview.html', ctx)


@login_required
def presence_for_group(req, gid):
    if req.method == 'POST':
        start = req.POST['start'] or None
        end = req.POST['end'] or None
    else:
        start = end = None
    try:
        gid = int(gid)
    except ValueError:
        messages.error(req, _(u'Group ID must be an integer.'))
        return redirect('core-presence')
    try:
        group = StudentGroup.objects.get(pk=gid)
    except StudentGroup.DoesNotExist:
        messages.error(req, _(u'Group with ID %d does not exist.' % gid))
        return redirect('core-presence')
    if end is None:
        end = date.today()
    else:
        end = datetime.strptime(end, '%d.%m.%Y').date()
    if start is None:
        d = date.today()
        start = date(d.year, d.month, 1)
    else:
        start = datetime.strptime(start, '%d.%m.%Y').date()
    if start > end:
        messages.error(_(u'End date before start date.'))
        return redirect('core-presence')
    req.session['presence_start'] = start
    req.session['presence_end'] = end
    dt = end - start
    _students = group.students.all().order_by('company__name', 'lastname')
    students = get_presence(_students, start, end)
    days = (start + timedelta(days=x) for x in xrange(dt.days + 1))
    ctx = dict(page_title=_(u'Presence for Group'), group=group,
        students=students, menus=menus, start=start, end=end,
        days=(x for x in days if x.weekday() not in (5, 6)),
        choices=[x[0] for x in PRESENCE_CHOICES], legend=PRESENCE_CHOICES[1:])
    return render(req, 'presence/group.html', ctx)


@permission_required('core.change_presenceday')
def presence_edit(req, student_id):
    _student = Student.objects.select_related().get(id=int(student_id))
    start = req.session.get('presence_start', date.today())
    end = req.session.get('presence_end', date.today())
    student, days = get_presence([_student], start, end)[0]
    ctx = dict(page_title=_(u'Presence for Student'), menus=menus,
        student=student, days=days, start=start, end=end,
        choices=PRESENCE_CHOICES)
    return render(req, 'presence/edit.html', ctx)


@login_required
def presence_printouts(req, job):
    groups = StudentGroup.objects.select_related().filter(job=job
        ).order_by('-start_date', 'job_short')
    jobs = StudentGroup.objects.values_list('job', flat=True)
    jobs = list(set(jobs))
    jobs.sort()
    ctx = dict(page_title=_(u'Presence %s' % job), menus=menus, jobs=jobs,
        groups=groups)
    return render(req, 'presence/list_printouts.html', ctx)


@login_required
def get_next_birthdays(req):
    days = int(req.GET.get('days', '14'))
    choice = [7, 14, 30, 90, 180]
    start = date.today()
    today = (start.month, start.day)
    dates = [start + timedelta(days=x) for x in xrange(days)]
    users = []
    students = []
    for d in dates:
        for p in UserProfile.objects.select_related(
            ).filter(birthdate__month=d.month, birthdate__day=d.day):
            p.today = (p.birthdate.month, p.birthdate.day) == today
            users.append(p)
        for s in Student.objects.select_related(
            ).filter(birthdate__month=d.month, birthdate__day=d.day):
            s.today = (s.birthdate.month, s.birthdate.day) == today
            students.append(s)
    ctx = dict(page_title=_(u'Next Birthdays'), menus=menus, users=users,
        students=students, choice=choice, days=days, today=start)
    return render(req, 'birthdays.html', ctx)


def barcode(req, format, barcode=''):
    if format == 'svg':
        bc = Code39(barcode, add_checksum=False)
        mimetype = 'image/svg+xml'
    else:
        if ImageWriter is None:
            return utils.error(req, _('PIL is not installed.'))
        bc = Code39(barcode, ImageWriter(), add_checksum=False)
        mimetype = 'image/{0}'.format(format)
    response = HttpResponse(mimetype=mimetype)
    try:
        bc.write(response, options={'format': format.upper()})
    except KeyError:
        return utils.error(req, _('Unsupported barcode format.'))
    return response
