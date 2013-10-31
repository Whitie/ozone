# -*- coding: utf-8 -*-

from django.forms import fields, widgets


class SearchInput5(widgets.Input):
    input_type = 'search'


class EmailInput5(widgets.Input):
    input_type = 'email'


class URLInput5(widgets.Input):
    input_type = 'url'


class DateInput5(widgets.DateInput):
    input_type = 'date'


class DateTimeInput5(widgets.DateTimeInput):
    input_type = 'datetime'
    format = '%Y-%m-%dT%H:%M:%SZ'


class TimeInput5(widgets.TimeInput):
    input_type = 'time'


class NumberInput5(widgets.Input):
    input_type = 'number'

    def __init__(self, attrs=None, min=None, max=None, step='any'):
        if attrs is None:
            attrs = {}
        if min is not None and 'min' not in attrs:
            attrs['min'] = min
        if max is not None and 'max' not in attrs:
            attrs['max'] = max
        if 'step' not in attrs:
            attrs['step'] = step
        super(NumberInput5, self).__init__(attrs)


class RangeInput5(NumberInput5):
    input_type = 'range'


class IntegerField5(fields.IntegerField):

    def __init__(self, max_value=None, min_value=None, step='any',
                 *args, **kw):
        fields.IntegerField.__init__(self, max_value, min_value, *args, **kw)
        self.widget = NumberInput5(min=min_value, max=max_value, step=step)


class IntegerRangeField5(IntegerField5):

    def __init__(self, max_value=None, min_value=None, step='any',
                 *args, **kw):
        IntegerField5.__init__(self, max_value, min_value, step, *args, **kw)
        self.widget = RangeInput5(min=min_value, max=max_value, step=step)
