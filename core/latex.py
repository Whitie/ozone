# -*- coding: utf-8 -*-

import os.path

import texescape

from subprocess import call

from django.conf import settings
from jinja2 import Environment, FileSystemLoader


texescape.init()


def tex_escape(text):
    return text.translate(texescape.tex_hl_escape_map_new)


def get_latex_env(template_path):
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader,
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    )
    env.filters['te'] = tex_escape
    return env


def get_latex_settings():
    s = settings.LATEX.copy()
    return s


def render_latex_to_pdf(filename, outdir=None):
    s = get_latex_settings()
    if outdir is None:
        outdir = s['outdir']
    filename = filename.replace('\\', '/')
    s['options'].append('-output-directory={0}'.format(outdir))
    cmd = [s['pdflatex']] + s['options'] + [filename]
    basename = os.path.splitext(filename)[0]
    outname = '{0}.pdf'.format(basename)
    print cmd
    ret1 = call(cmd)
    ret2 = call(cmd)
    return (os.path.join(outdir, outname), ret1, ret2)
