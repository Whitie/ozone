#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from datetime import date as _date, timedelta


DAYS = {
    0: u'Montag',
    1: u'Dienstag',
    2: u'Mittwoch',
    3: u'Donnerstag',
    4: u'Freitag',
    5: u'Samstag',
    6: u'Sonntag',
}


def easter_sunday(year):
    k = year / 100
    m = 15 + (3 * k + 3) / 4 - (8 * k + 13) / 25
    s = 2 - (3 * k + 3) / 4
    a = year % 19
    d = (19 * a + m) % 30
    r = (d + a / 11) / 29
    og = 21 + d - r
    sz = 7 - (year + year / 4 + s) % 7
    oe = 7 - (og - sz) % 7
    os = og + oe
    return _date(year, 3, 1) + timedelta(days=os - 1)


special_days = {
    # Feste Feiertage
    'Neujahrstag': lambda year: _date(year, 1, 1),
    'Tag der Arbeit': lambda year: _date(year, 5, 1),
    'Tag der Deutschen Einheit': lambda year: _date(year, 10, 3),
    'Erster Weihnachtstag': lambda year: _date(year, 12, 25),
    'Zweiter Weihnachtstag': lambda year: _date(year, 12, 26),
    # Bewegliche Feiertage
    'Karfreitag': lambda year: easter_sunday(year) - timedelta(days=2),
    'Ostersonntag': lambda year: easter_sunday(year),
    'Ostermontag': lambda year: easter_sunday(year) + timedelta(days=1),
    'Himmelfahrt': lambda year: easter_sunday(year) + timedelta(days=39),
    'Pfingstsonntag': lambda year: easter_sunday(year) + timedelta(days=49),
    'Pfingstmontag': lambda year: easter_sunday(year) + timedelta(days=50),
}


def is_special_day(date, include_weekend=False):
    if include_weekend:
        if date.weekday() == 5 or date.weekday() == 6:
            return True
    days = [x(date.year) for x in special_days.values()]
    if date in days:
        return True
    else:
        return False


def test():
    import unittest

    class SpecialDaysTest(unittest.TestCase):
        def test_fester_Feiertag(self):
            d = _date(2015, 12,25)
            d2 = special_days['Erster Weihnachtstag'](2015)
            self.assertEqual(d, d2)
        def test_ist_Feiertag_1(self):
            d = _date(2012, 12, 26)
            self.assertTrue(is_special_day(d))
        def test_ist_Feiertag_2(self):
            d = _date(2020, 5, 1)
            self.assertTrue(is_special_day(d))
        def test_ist_kein_Feiertag(self):
            d = _date(2013, 5, 14)
            self.assertFalse(is_special_day(d))
        def test_ist_Wochenende(self):
            d = _date(2013, 5, 18)
            self.assertTrue(is_special_day(d, include_weekend=True))
        def test_ist_Ostersonntag_1(self):
            d = _date(2014, 4, 20)
            self.assertEqual(d, easter_sunday(2014))
        def test_ist_Ostersonntag_2(self):
            d = _date(2020, 4, 12)
            self.assertEqual(d, easter_sunday(2020))

    suite = unittest.TestLoader().loadTestsFromTestCase(SpecialDaysTest)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        year = int(sys.argv[1])
        days = [(x, y(year)) for x, y in special_days.items()]
        days.sort(key=lambda x: x[1])
        for name, date in days:
            print '{0:<30}{1:<15} {2}'.format(
                name, date.strftime('%d.%m.%Y'), DAYS[date.weekday()])
    else:
        test()

