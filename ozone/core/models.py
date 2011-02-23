# -*- coding: utf-8 -*-

import json

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from core.utils import named


class Part(models.Model):
    name = models.CharField(_(u'Name'), max_length=30)
    description = models.TextField(_(u'Description'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Part')
        verbose_name_plural = _(u'Parts')


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=_(u'User'), editable=False)
    name_prefix = models.CharField(_(u'Name Prefix'), max_length=12,
        blank=True)
    street = models.CharField(_(u'Street'), max_length=100, blank=True)
    zip_code = models.CharField(_(u'Zip Code'), max_length=10, blank=True)
    city = models.CharField(_(u'City'), max_length=100, blank=True)
    country = models.CharField(_(u'Country'), max_length=50, blank=True)
    phone = models.CharField(_(u'Phone'), max_length=30, blank=True)
    mobile = models.CharField(_(u'Mobile'), max_length=30, blank=True)
    part = models.ForeignKey(Part, verbose_name=_(u'Part'), blank=True,
        null=True)
    can_login = models.BooleanField(_(u'Can Login'), default=True)
    _config = models.TextField(blank=True, editable=False, default='')

    def __unicode__(self):
        name = self.user.get_full_name()
        if name:
            return u'{0} {1}'.format(self.name_prefix, name)
        return self.user.username

    def config(self):
        if not self._config:
            return dict()
        return json.loads(self._config)

    def set_config(self, config):
        if not isinstance(config, dict):
            raise ValueError('Config must be dict object.')
        self._config = json.dumps(config)

    def set_value(self, key, value=None):
        c = self.config()
        c[key] = value
        self.set_config(c)

    class Meta:
        verbose_name = _(u'Profile')
        verbose_name_plural = _(u'Profiles')


class News(models.Model):
    title = models.CharField(_(u'Title'), max_length=50)
    text = models.TextField(_(u'Text'))
    date = models.DateTimeField(_(u'Date'), auto_now_add=True)
    author = models.ForeignKey(User, verbose_name=_(u'Author'))
    public = models.BooleanField(_(u'Public'), default=True)

    def __unicode__(self):
        if len(self.title) < 40:
            return self.title
        return u'{0}...'.format(self.title[:40])

    class Meta:
        verbose_name = _(u'News')
        verbose_name_plural = _(u'News')
        get_latest_by = 'date'
        ordering = ('-date', 'author')


class Company(models.Model):
    name = models.CharField(_(u'Name'), max_length=100)
    short_name = models.CharField(_(u'Short Name'), max_length=10, blank=True)
    street = models.CharField(_(u'Street'), max_length=100, blank=True)
    zip_code = models.CharField(_(u'Zip Code'), max_length=10, blank=True)
    city = models.CharField(_(u'City'), max_length=100, blank=True)
    country = models.CharField(_(u'Country'), max_length=50, blank=True)
    phone = models.CharField(_(u'Phone'), max_length=30, blank=True)
    fax = models.CharField(_(u'Fax'), max_length=30, blank=True)
    customer_number = models.CharField(_(u'Customer Number'), max_length=50,
        blank=True)
    web = models.URLField(_(u'Web'), blank=True)
    qm_rating = models.CharField(_(u'QM Rating'), max_length=1, blank=True)
    qm_note = models.TextField(_(u'QM Note'), blank=True)

    def __unicode__(self):
        if self.short_name:
            return u'{0} ({1})'.format(self.name, self.short_name)
        return self.name

    def has_students(self):
        return bool(self.students.count())

    class Meta:
        verbose_name = _(u'Company')
        verbose_name_plural = _(u'Companies')
        ordering = ('name',)


class Contact(models.Model):
    name_prefix = models.CharField(_(u'Name Prefix'), max_length=12)
    lastname = models.CharField(_(u'Lastname'), max_length=50)
    firstname = models.CharField(_(u'Firstname'), max_length=50)
    function = models.CharField(_(u'Function'), max_length=50, blank=True)
    phone = models.CharField(_(u'Phone'), max_length=30, blank=True)
    email = models.EmailField(_(u'Email'), blank=True)
    note = models.TextField(_(u'Note'), blank=True)
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='contacts')

    def __unicode__(self):
        s = u'{0} {1} {2}'.format(self.name_prefix, self.firstname,
                                  self.lastname)
        if self.function:
            return u'{0} ({1})'.format(s, self.function)
        return s

    class Meta:
        verbose_name = _(u'Contact')
        verbose_name_plural = _(u'Contacts')


class StudentGroup(models.Model):
    start_date = models.DateField(_(u'Start Date'))
    job = models.CharField(_(u'Job'), max_length=50, blank=True)
    job_short = models.CharField(_(u'Job Short'), max_length=10,
        help_text=_(u'This field will be converted to uppercase.'))

    @named(_(u'Groupname'))
    def name(self):
        return u'{0} {1}'.format(self.job_short, self.start_date.strftime('%Y'))

    def __unicode__(self):
        return self.name()

    def finished(self):
        return all([x.finished for x in self.students.all()])

    def save(self, *args, **kwargs):
        self.job_short = self.job_short.upper()
        super(StudentGroup, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u'Group')
        verbose_name_plural = _(u'Groups')
        ordering = ['-start_date', 'job']


SEX_CHOICES = (('M', _(u'Male')), ('F', _(u'Female')))

class Student(models.Model):
    lastname = models.CharField(_(u'Lastname'), max_length=50)
    firstname = models.CharField(_(u'Firstname'), max_length=50)
    sex = models.CharField(_(u'Sex'), max_length=1, choices=SEX_CHOICES)
    birthdate = models.DateField(_(u'Birthdate'))
    picture = models.ImageField(_(u'Picture'), upload_to='pictures', blank=True)
    street = models.CharField(_(u'Street'), max_length=100, blank=True)
    zip_code = models.CharField(_(u'Zip Code'), max_length=10, blank=True)
    city = models.CharField(_(u'City'), max_length=100, blank=True)
    country = models.CharField(_(u'Country'), max_length=50, blank=True)
    email = models.EmailField(_(u'Email'), blank=True)
    phone = models.CharField(_(u'Phone'), max_length=30, blank=True)
    mobile = models.CharField(_(u'Mobile'), max_length=30, blank=True)
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='students', blank=True, null=True)
    group = models.ForeignKey(StudentGroup, verbose_name=_(u'Group'),
        related_name='students', blank=True, null=True)
    cabinet = models.CharField(_(u'Cabinet'), max_length=20, blank=True)
    key = models.CharField(_(u'Key'), max_length=20, blank=True)
    test_result = models.PositiveSmallIntegerField(_(u'Test Result'),
        blank=True, null=True)
    test_date = models.DateField(_(u'Test Date'), blank=True, null=True)
    exam_1 = models.PositiveSmallIntegerField(_(u'Exam 1'), blank=True,
        null=True)
    exam_1_weight = models.PositiveSmallIntegerField(_(u'Exam 1 weight'),
        blank=True, null=True, default=30)
    exam_2 = models.PositiveSmallIntegerField(_(u'Exam 2'), blank=True,
        null=True)
    barcode = models.CharField(_(u'Barcode'), max_length=50, blank=True,
        editable=False)
    finished = models.BooleanField(_(u'Finished'), default=False)

    def __unicode__(self):
        return u'{0}, {1} ({2})'.format(self.lastname, self.firstname,
                                        self.group.name())

    def barcode_url(self):
        url = '/'.join([settings.MEDIA_URL.rstrip('/'), 'barcodes',
                        '%s.png' % self.barcode])
        return url

    def final_grade(self):
        if self.exam_1 and self.exam_2:
            weighted = self.exam_1 * self.exam_1_weight + \
                       self.exam_2 * (100 - self.exam_1_weight)
            return int(round(weighted / 100.0, 0))

    class Meta:
        verbose_name = _(u'Student')
        verbose_name_plural = _(u'Students')


class Memo(models.Model):
    student = models.ForeignKey(Student, verbose_name=_(u'Student'),
        related_name='memos')
    text = models.TextField(_(u'Text'))
    created = models.DateTimeField(_(u'Created'), auto_now_add=True)
    created_by = models.ForeignKey(User, verbose_name=_(u'Created by'))

    def __unicode__(self):
        if len(self.text) > 40:
            dots = u'...'
        else:
            dots = u''
        return u'[{0}] {1}: {2}{3}'.format(self.created.strftime('%x'),
                                           self.student, self.text[:40], dots)

    class Meta:
        verbose_name = _(u'Memo')
        verbose_name_plural = _(u'Memos')
