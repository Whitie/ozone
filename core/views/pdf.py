# -*- coding: utf-8 -*-

import codecs
import os

from calendar import monthrange
from datetime import date, timedelta

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
from core.models import (Student, StudentGroup, PresencePrintout, Company,
                         PresenceDay, UserProfile)
from core.forms import PresenceForm


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.normpath(
    os.path.join(PATH, '..', 'templates', 'latex'))


def iter_days(start, days):
    for i in xrange(days):
        yield start + timedelta(days=i)


def make_latex(ctx, template, company=None):
    env = latex.get_latex_env(TEMPLATE_PATH)
    s = latex.get_latex_settings()
    tpl = env.get_template(template)
    if company is not None:
        name = '{0}_{1}_{2}'.format(unicode(ctx['group']), company.short_name,
            template)
    else:
        name = '{0}_{1}'.format(unicode(ctx['group']), template)
    filename = os.path.join(s['build_dir'], name)
    try:
        os.remove(filename)
    except:
        pass
    with codecs.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(tpl.render(**ctx))
    pdfname, r1, r2 = latex.render_latex_to_pdf(filename)
    return pdfname


def get_presence_context(gid, year, month):
    group = StudentGroup.objects.get(id=gid)
    ctx = dict(group=group)
    days_of_month = monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, days_of_month)
    ctx['day_nums'] = [x.day for x in iter_days(start, days_of_month)
                       if x.weekday() not in (5, 6)]
    ctx['edu_year'] = utils.get_edu_year(group.start_date)
    ctx['timespan'] = unicode(start.strftime('%m/%Y'))
    ctx['table_days'] = [u'c' for x in ctx['day_nums']]
    return ctx


@login_required
def pdf(req, what='grouplist'):
    response = HttpResponse(mimetype='application/pdf')
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
def generate_presence_clean(req, gid, year, month):
    ctx = get_presence_context(int(gid), int(year), int(month))
    ctx['students'] = Student.objects.filter(group=ctx['group']
        ).order_by('company__short_name', 'lastname')
    ctx['s'] = latex.get_latex_settings()
    ctx['schooldays'] = u''
    ctx['instructor'] = unicode(req.user.get_profile())
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
    ts = date(int(year), int(month), 1)
    group = StudentGroup.objects.select_related().get(id=int(gid))
    companies = []
    for s in group.students.all():
        if s.company not in companies:
            count = s.company.students.filter(finished=False).count()
            s.company.group_count = count
            printouts = PresencePrintout.objects.filter(company=s.company,
                date=ts)
            s.company.currents = printouts
            companies.append(s.company)
    show = False
    if req.method == 'POST':
        form = PresenceForm(req.POST)
        if form.is_valid():
            instructor = User.objects.get(id=form.cleaned_data['instructor'])
            course = form.cleaned_data['course']
            school_days = form.cleaned_data['school_days']
            show = True
        else:
            messages.error(req, u'Bitte korrigieren Sie die Pflichtfelder.')
    else:
        form = PresenceForm()
    ctx = dict(page_title=_(u'Presence PDF-Generation'), menus=menus,
        instructor=instructor, course=course, school_days=school_days,
        group=group, show=show, ts=ts, form=form, companies=companies,
        year=year, month=month)
    return render(req, 'presence/generate_pdf.html', ctx)


@utils.json_rpc
def generate_presence_pdf(req, data):
    user = User.objects.get(id=data['uid'])
    company = Company.objects.get(id=data['cid'])
    ctx = get_presence_context(data['gid'], data['year'], data['month'])
    students = Student.objects.select_related().filter(
        group=ctx['group'], company=company).order_by('lastname')
    k = 0
    whole = 0
    for s in students:
        days = []
        notes = []
        for num in ctx['day_nums']:
            try:
                d = PresenceDay.objects.get(student=s,
                    date=date(data['year'], data['month'], num))
                if d.entry in (u'K', u'T'):
                    k += 1
                elif d.entry in (u'*',):
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
            days.append(u'\\tiny{%s}' %
                (latex.tex_escape(u', '.join(notes)),))
        else:
            days.append(u'')
        s.days = days
    ctx['students'] = students
    ctx['k'] = k
    ctx['whole'] = whole
    ctx['s'] = latex.get_latex_settings()
    ctx['schooldays'] = data['sdays']
    ctx['instructor'] = unicode(user.get_profile())
    ctx['course'] = data['course']
    ctx['empty'] = False
    print ctx
    fullname = make_latex(ctx, 'awhl.tex', company)
    filename = os.path.split(fullname)[1]
    d = date(data['year'], data['month'], 1)
    printout, created = PresencePrintout.objects.get_or_create(
        company=company, group=ctx['group'], date=d)
    with open(fullname, 'rb') as fp:
        content = ContentFile(fp.read())
    printout.pdf.save(filename, content)
    printout.save()
    return {'url': printout.pdf.url, 'name': filename}
