# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from core.models import News
from core.forms import NewsForm
from core.menu import menus

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
    ctx = dict(page_title=_(u'bbz Tools Overview'), menus=menus, news=news)
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
            return redirect('/core/')
        messages.error(req, _(u'Please correct the wrong fields.'))
    else:
        form = NewsForm()
    ctx = dict(page_title=_(u'Add News'), menus=menus, form=form)
    return render_to_response('news/add.html', ctx,
                              context_instance=RequestContext(req))
