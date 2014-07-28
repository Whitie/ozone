# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from datetime import date, timedelta

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from core.utils import render, charts
from core.models import AccidentEntry, Student, VIOLATION_CHOICES
from core.forms import AccidentForm
from core.views import helper as h
from core.menu import menus


# Functions
def _get_accident_chart_all():
    dt = date.today()
    start_dt = dt - timedelta(days=4 * 365)
    labels = []
    accidents = []
    way = []
    for year in range(start_dt.year, dt.year + 1):
        q = AccidentEntry.objects.filter(date_time__year=year)
        labels.append(unicode(year))
        accidents.append(q.count())
        way.append(q.filter(violation=1).count())
    barchart = charts.MyBarChart((labels, accidents, way))
    return barchart


def _get_accident_chart(year):
    q = AccidentEntry.objects.filter(date_time__year=year)
    _all = q.count()
    stat = []
    for num, label in VIOLATION_CHOICES:
        tmp = q.filter(violation=num).count()
        pc = (tmp / _all) * 100.0
        stat.append((pc, unicode(label)))
    stat.sort(key=lambda x: x[0], reverse=True)
    piechart = charts.LegendedPie3d(stat)
    return piechart


# Views for accidents

@login_required
def accidents_index(req):
    today = date.today()
    accidents = AccidentEntry.objects.filter(date_time__year=today.year
        ).order_by('-date_time')
    ctx = dict(page_title=u'Unfälle', subtitle=u'dieses Jahr', dt=True,
        accidents=accidents, menus=menus, dp=True, need_ajax=True, old=False)
    return render(req, 'accidents/index.html', ctx)


@login_required
def accident_details(req, id):
    accident = AccidentEntry.objects.select_related().get(pk=int(id))
    ctx = dict(page_title=u'Unfalldatenblatt', ac=accident, menus=menus)
    if accident.is_employee:
        ctx['pr'] = accident.employee.userprofile
    return render(req, 'accidents/details.html', ctx)


@login_required
def old_accidents(req):
    today = date.today()
    older = today - timedelta(days=365)
    accidents = AccidentEntry.objects.filter(date_time__lt=older
        ).order_by('-date_time')
    ctx = dict(page_title=u'Ältere Unfälle', accidents=accidents, menus=menus,
        old=True, dt=True)
    return render(req, 'accidents/index.html', ctx)


@login_required
def accidents_statistics(req):
    dt = date.today()
    start_dt = dt - timedelta(days=4 * 365)
    accidents = []
    for year in range(start_dt.year, dt.year + 1):
        q = AccidentEntry.objects.filter(date_time__year=year)
        accidents.append(
            (year, q.count(), q.filter(violation=1).count())
        )
    ctx = dict(page_title='Unfallstatistik', menus=menus, year=dt.year,
        accidents=accidents, start=start_dt.year)
    return render(req, 'accidents/statistics/index.html', ctx)


@login_required
def accident_add(req):
    form = AccidentForm()
    form.fields['student'].queryset = Student.objects.filter(
        finished=False).order_by('lastname')
    form.fields['employee'].queryset = User.objects.exclude(
        username='admin').order_by('last_name')
    return render(req, 'accidents/add.html', {'form': form})


def img_all(req):
    try:
        chart = _get_accident_chart_all()
    except:
        chart = charts.NoData()
    bin_image = chart.asString('png')
    return HttpResponse(bin_image, content_type='image/png')


def img_accidents_by_year(req, year=None):
    try:
        year = int(year)
    except TypeError:
        year = date.today().year
    try:
        chart = _get_accident_chart(year)
    except:
        chart = charts.NoData()
    bin_image = chart.asString('png')
    return HttpResponse(bin_image, content_type='image/png')
