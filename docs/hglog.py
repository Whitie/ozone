#!/usr/bin/python2
# -*- coding: utf-8 -*-

import codecs
import os

from datetime import datetime
from string import Template
from subprocess import Popen, PIPE
from textwrap import TextWrapper


PATH = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(PATH, 'changelog.rst.tpl')
OUT = os.path.join(PATH, 'changelog.rst')
CMD = ['hg', 'log']
ENC = 'utf-8'


def get_log():
    proc = Popen(CMD, stdout=PIPE)
    output = proc.communicate()[0]
    return output.decode(ENC)


def indent(text, level=4):
    ind = ' ' * level
    wrapper = TextWrapper(initial_indent=ind, subsequent_indent=ind)
    new = []
    for line in text.split('\n'):
        new.append(wrapper.fill(line))
    return '\n'.join(new)


def main():
    with codecs.open(TPL, encoding='utf-8') as f:
        tpl = Template(f.read())
    log = get_log()
    now = datetime.now()
    data = dict(hglog=indent(log), now=now.strftime('%d.%m.%Y %H:%M:%S'))
    with codecs.open(OUT, 'w', encoding='utf-8') as f:
        f.write(tpl.safe_substitute(data))


if __name__ == '__main__':
    main()

