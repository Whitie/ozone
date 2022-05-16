# -*- coding: utf-8 -*-

import codecs
import os

from calendar import monthrange
from datetime import date, datetime, timedelta
from itertools import izip_longest
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages

from core import utils
from core import latex
from core.menu import menus
from core.views import helper as h
from core.models import (Student, StudentGroup, PresencePrintout, Company,
                         PresenceDay, UserProfile, PDFPrintout)
from core.forms import PresenceForm, get_user


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.normpath(
    os.path.join(PATH, '..', 'templates', 'latex'))
BBZLOGO = os.path.join(TEMPLATE_PATH, 'bbzlogo.png')
ILBLOGO = os.path.join(TEMPLATE_PATH, 'ilblogo.png')
DAYS = {
    0: u'Montag',
    1: u'Dienstag',
    2: u'Mittwoch',
    3: u'Donnerstag',
    4: u'Freitag',
    5: u'Sonnabend',
    6: u'Sonntag',
}
MAX_ITEMS = 26


def iter_days(start, days):
    for i in xrange(days):
        yield start + timedelta(days=i)


def make_latex(ctx, template, company=None, name=None):
    env = latex.get_latex_env(TEMPLATE_PATH)
    s = latex.get_latex_settings()
    tpl = env.get_template(template)
    if name is None:
        if company is not None:
            name = u'{0}_{1}_{2}'.format(
                company.short_name, unicode(ctx['group']), template
            )
        else:
            name = u'{0}_{1}'.format(unicode(ctx['group']), template)
    else:
        name = u'{0}_{1}'.format(name, template)
    name = utils.secure_filename(name)
    filename = os.path.join(s['build_dir'], name)
    try:
        os.remove(filename)
    except:  # noqa: E722
        pass
    ctx['BBZLOGO'] = BBZLOGO
    ctx['ILBLOGO'] = ILBLOGO
    with codecs.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(tpl.render(**ctx))
    pdfname, r1, r2 = latex.render_latex_to_pdf(filename)
    return pdfname


def get_presence_context(gid, year, month):
    try:
        group = StudentGroup.objects.get(id=gid)
    except:  # noqa: E722
        group = None
    ctx = dict(group=group)
    days_of_month = monthrange(year, month)[1]
    start = date(year, month, 1)
    ctx['day_nums'] = []
    try:
        ctx['edu_year'] = utils.get_edu_year(group.start_date)
    except AttributeError:
        ctx['edu_year'] = u'-'
    ctx['timespan'] = unicode(start.strftime('%m/%Y'))
    tmp = []
    for x in iter_days(start, days_of_month):
        wd = x.weekday()
        if wd not in (5, 6):
            ctx['day_nums'].append(x.day)
            if wd == 4:
                tmp.extend([u'c', u'||'])
            else:
                tmp.extend([u'c', u'|'])
    ctx['table_days'] = tmp[:-1]
    return ctx


@login_required
def pdf(req, what='grouplist'):
    response = HttpResponse(content_type='application/pdf')
    return response


@login_required
def generate_phonelist(req):
    profiles = UserProfile.objects.select_related().exclude(
        user__username='admin').filter(
        external=False).order_by('user__last_name')
    # Workaround to use make_latex function
    ctx = dict(profiles=profiles, group='tmp')
    filename = make_latex(ctx, 'phonelist.tex')
    with open(filename, 'rb') as fp:
        response = HttpResponse(fp.read(), content_type='application/pdf')
    return response


@login_required
def student_detail(req, sid):
    student = Student.objects.select_related().get(id=int(sid))
    ctx = dict(s=student, birthdate=student.birthdate.strftime('%d.%m.%Y'),
               group='tmp')
    filename = make_latex(ctx, 'student_detail.tex')
    with open(filename, 'rb') as fp:
        response = HttpResponse(fp.read(), content_type='application/pdf')
    return response


@login_required
def generate_presence_clean(req, gid, year, month):
    ctx = get_presence_context(int(gid), int(year), int(month))
    try:
        ctx['students'] = h.sort_students_for_presence(ctx['group'].students)
    except AttributeError:
        s = h.get_students(req.user)
        ctx['students'] = h.sort_students_for_presence(s)
    ctx['s'] = latex.get_latex_settings()
    ctx['schooldays'] = u''
    ctx['instructor'] = unicode(req.user.userprofile)
    ctx['course'] = u''
    ctx['empty'] = True
    filename = make_latex(ctx, 'awhl.tex')
    with open(filename, 'rb') as fp:
        response = HttpResponse(fp.read(), content_type='application/pdf')
    return response


@login_required
def generate_presence_filled(req, gid, year, month):
    instructor = None
    course = None
    school_days = None
    incl_sup = None
    ts = date(int(year), int(month), 1)
    group = StudentGroup.objects.select_related().get(id=int(gid))
    companies = []
    for s in group.students.filter(finished=False):
        if s.company not in companies:
            count = s.company.students.filter(
                finished=False, group=group).count()
            s.company.group_count = count
            printouts = PresencePrintout.objects.filter(
                company=s.company, date=ts)
            s.company.currents = printouts
            companies.append(s.company)
    show = False
    if req.method == 'POST':
        form = PresenceForm(req.POST)
        form.fields['instructor'].choices = get_user()
        if form.is_valid():
            instructor = User.objects.get(id=form.cleaned_data['instructor'])
            course = form.cleaned_data['course']
            school_days = form.cleaned_data['school_days']
            incl_sup = form.cleaned_data['include_supported_days']
            show = True
        else:
            messages.error(req, u'Bitte korrigieren Sie die Pflichtfelder.')
    else:
        form = PresenceForm(initial={'include_supported_days': True})
        form.fields['instructor'].choices = get_user()
    ctx = dict(
        page_title=_(u'Presence PDF-Generation'), menus=menus,
        instructor=instructor, course=course, school_days=school_days,
        group=group, show=show, ts=ts, form=form, companies=companies,
        year=year, month=month, incl_sup=incl_sup, need_ajax=True
    )
    return render(req, 'presence/generate_pdf.html', ctx)


def _prepare_students(students, ctx, data):
    k = 0
    whole = 0
    for s in students:
        days = []
        notes = []
        for num in ctx['day_nums']:
            try:
                d = PresenceDay.objects.get(
                    student=s, date=date(data['year'], data['month'], num)
                )
                if d.entry == u'A':
                    d.entry = u'*'
                if d.entry in (u'K', u'T'):
                    k += 1
                elif d.entry in (u'*', u'A', u'AC', u'W'):
                    whole += 1
                if d.lateness:
                    days.append(u'$%s_{%d}$' % (
                        latex.tex_escape(d.entry), d.lateness))
                else:
                    days.append(latex.tex_escape(d.entry))
                if d.note:
                    notes.append(u'{0} {1}'.format(
                        d.date.strftime('%d.%m.'), d.note))
            except PresenceDay.DoesNotExist:
                days.append(u'')
        if notes:
            days.append(
                u'\\tiny{%s}' % (latex.tex_escape(u', '.join(notes)),)
            )
        else:
            days.append(u'')
        s.days = days
    return students, k, whole


@utils.json_rpc
def generate_presence_pdf(req, data):
    user = User.objects.get(id=data['uid'])
    ctx = get_presence_context(data['gid'], data['year'], data['month'])
    student_filter = dict(group=ctx['group'], finished=False)
    student_sort = ['lastname']
    if data['cid']:
        gen_all = False
        company = Company.objects.get(id=data['cid'])
        student_filter['company'] = company
    else:
        gen_all = True
        company = Company.objects.get(short_name=u'Alle')
        student_sort.insert(0, 'company__name')
    ctx['incl_sup'] = data['incl_sup']
    ctx['company'] = company
    start = date(data['year'], data['month'], 1)
    end = start + timedelta(days=30)
    _students = Student.objects.select_related().filter(
        **student_filter).order_by(*student_sort)
    students = [x[0] for x in h.get_presence(_students, start, end)]
    students, k, whole = _prepare_students(students, ctx, data)
    ctx['students'] = students
    ctx['k'] = k
    ctx['whole'] = whole
    ctx['s'] = latex.get_latex_settings()
    ctx['schooldays'] = data['sdays']
    ctx['instructor'] = unicode(user.userprofile)
    ctx['course'] = data['course']
    ctx['empty'] = False
    fullname = make_latex(ctx, 'awhl.tex', company)
    filename = os.path.split(fullname)[1]
    printout, created = PresencePrintout.objects.get_or_create(
        company=company, group=ctx['group'], date=start)
    with open(fullname, 'rb') as fp:
        content = ContentFile(fp.read())
    printout.pdf.save(filename, content)
    printout.save()
    ret = {'url': printout.pdf.url, 'name': filename}
    if gen_all:
        full_name = make_latex(ctx, 'awhl_einzeln.tex', company)
        file_name = os.path.split(full_name)[1]
        pdf = PDFPrintout.objects.create(category=u'Einzel-AWHL')
        with open(full_name, 'rb') as fp:
            content = ContentFile(fp.read())
        pdf.pdf.save(file_name, content)
        pdf.save()
        ret['surl'] = pdf.pdf.url
        ret['sname'] = file_name
    return ret


def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]


def _split_days(days):
    chunks = list(_chunks(days, MAX_ITEMS))
    if len(chunks) % 2 != 0:
        chunks.append([(u'', u'')] * len(chunks[0]))
    tmp = []
    for i in xrange(0, len(chunks), 2):
        tmp.append(
            list(izip_longest(chunks[i], chunks[i+1], fillvalue=(u'', u'')))
        )
    return tmp


@utils.json_rpc
def generate_ilb_for_group(req, data):
    students = req.session.get('selected_students', [])
    items = []
    days = [datetime.strptime(x, '%Y-%m-%d') for x in data['dates']]
    dy = [(DAYS[x.weekday()], unicode(x.strftime('%d.%m.%Y'))) for x in days]
    dy = _split_days(dy)
    for sid in students:
        s = Student.objects.select_related().get(id=sid)
        ctx = dict(student=s, days=dy)
        ctx.update(data)
        print(ctx)
        full_name = make_latex(ctx, 'ilb_azubi.tex', name=s.lastname)
        file_name = os.path.split(full_name)[1]
        pdf = PDFPrintout.objects.create(category=u'ILB-Azubi')
        with open(full_name, 'rb') as fp:
            content = ContentFile(fp.read())
        pdf.pdf.save(file_name, content)
        pdf.save()
        items.append(
            u'<li><a href="{0}" target="_blank">{1}</a></li>'
            u''.format(pdf.pdf.url, file_name)
        )
    return {'files': items}


# Alias will be removed in 4.0
generate_presence_pdf_all = generate_presence_pdf
