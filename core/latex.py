# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

import texescape

from subprocess import call

from django.conf import settings
from jinja2 import Environment, FileSystemLoader

from core.models import Configuration


texescape.init()


def tex_escape(text):
    try:
        return text.translate(texescape.tex_hl_escape_map_new)
    except:  # noqa: E722
        return ''


def escape_path(path):
    if os.name != 'nt':
        return path
    else:
        return path.replace('\\', '/')


def get_latex_env(template_path):
    loader = FileSystemLoader(template_path)
    env = Environment(
        loader=loader,
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    )
    env.filters['te'] = tex_escape
    env.filters['pe'] = escape_path
    return env


def get_latex_settings():
    c = Configuration.objects.all().order_by('id').last()
    s = {
        'pdflatex': c.pdflatex,
        'options': c.latex_options.split(),
        'build_dir': settings.LATEX_BUILD_DIR,
        'fromfax': c.fax,
        'fromphone': c.phone,
        'fromname': c.name,
        'fromaddress': '{0.street}, {0.zip_code} {0.city}'.format(c),
        'fromlogo': c.logo.path,
        'country': c.country,
        'app_config': c,
    }
    return s


def clean_build_dir(directory):
    for f in os.listdir(directory):
        ext = os.path.splitext(f)[1]
        if ext not in ('.sty', '.tex'):
            try:
                os.remove(os.path.join(directory, f))
            except:  # noqa: E722
                pass


def render_latex_to_pdf(filename, build_dir=None):
    s = get_latex_settings()
    if build_dir is None:
        build_dir = s['build_dir']
    clean_build_dir(build_dir)
    build_dir = escape_path(build_dir)
    filename = escape_path(filename)
    s['options'].append('-output-directory={0}'.format(build_dir))
    cmd = [s['pdflatex']] + s['options'] + [filename]
    basename = os.path.splitext(filename)[0]
    outname = '{0}.pdf'.format(basename)
    ret1 = call(cmd)
    ret2 = call(cmd)
    return (os.path.join(build_dir, outname), ret1, ret2)
