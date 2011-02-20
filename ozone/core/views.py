# -*- coding: utf-8 -*-

import string

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from core.models import News, Company, Student, StudentGroup
from core.forms import NewsForm, SearchForm, StudentSearchForm
from core.menu import menus
from barcode import get_barcode

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
    return render_to_response('index.html', ctx,
                              context_instance=RequestContext(req))


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
    return render_to_response('news/add.html', ctx,
                              context_instance=RequestContext(req))


def do_login(req):
    if req.method == 'POST':
        form = AuthenticationForm(req, req.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                p = user.get_profile()
                if user.is_active and p.can_login:
                    login(req, user)
                    messages.success(req, _(u'Login accepted.'))
                    return redirect('/')
                else:
                    messages.error(req, _(u'Account is disabled.'))
            else:
                messages.error(req, _(u'Username and/or password incorrect.'))
    else:
        form = AuthenticationForm()
        req.session.set_test_cookie()
    ctx = dict(page_title=_(u'Login Page'), form=form)
    return render_to_response('login.html', ctx,
                              context_instance=RequestContext(req))


def do_logout(req):
    logout(req)
    messages.success(req, _(u'Logged out.'))
    return redirect('/')


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
        startchar=startchar, chars=string.ascii_uppercase, form=form)
    return render_to_response('companies/list.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def list_students(req, startchar=''):
    if req.method == 'POST':
        form = StudentSearchForm(req.POST)
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
        if not startchar:
            students = Student.objects.select_related().all()
            for c in string.ascii_uppercase:
                students = students.exclude(lastname__istartswith=c)
        else:
            students = Student.objects.select_related().filter(
                lastname__istartswith=startchar)
    students = students.filter(finished=False)
    ctx = dict(page_title=_(u'Students'), students=students, menus=menus,
        startchar=startchar, chars=string.ascii_uppercase, form=form)
    return render_to_response('students/list.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def list_groups(req):
    groups = StudentGroup.objects.select_related().filter(finished=False)
    ctx = dict(page_title=_(u'Groups'), groups=groups, menus=menus)
    return render_to_response('students/groups.html', ctx,
                              context_instance=RequestContext(req))


@login_required
def group_details(req, gid):
    pass


def barcode(req, barcode='0'):
    code = get_barcode('code39', barcode)
    response = HttpResponse(mimetype='image/svg+xml')
    code.write(response)
    return response

