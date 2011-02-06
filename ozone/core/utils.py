# -*- coding: utf-8 -*-


def named(verbose_name):
    def decorate(f):
        f.short_description = verbose_name
        return f
    return decorate

