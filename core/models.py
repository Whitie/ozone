# -*- coding: utf-8 -*-

import json

from datetime import date
from mimetypes import guess_type

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from audit_log.models.managers import AuditLog
from core.utils import named


class CommonInfo(models.Model):
    street = models.CharField(_(u'Street'), max_length=100, blank=True)
    zip_code = models.CharField(_(u'Zip Code'), max_length=15, blank=True)
    city = models.CharField(_(u'City'), max_length=100, blank=True)
    country = models.CharField(_(u'Country'), max_length=50, blank=True)
    phone = models.CharField(_(u'Phone'), max_length=30, blank=True)

    class Meta:
        abstract = True


class Part(models.Model):
    name = models.CharField(_(u'Name'), max_length=30)
    description = models.TextField(_(u'Description'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Part')
        verbose_name_plural = _(u'Parts')


class UserProfile(CommonInfo):
    user = models.OneToOneField(User, verbose_name=_(u'User'), editable=False)
    name_prefix = models.CharField(_(u'Name Prefix'), max_length=12,
        blank=True)
    birthdate = models.DateField(_(u'Birthdate'), null=True, blank=True)
    mobile = models.CharField(_(u'Mobile'), max_length=30, blank=True)
    part = models.ForeignKey(Part, verbose_name=_(u'Part'), blank=True,
        null=True, related_name='profiles')
    subjects = models.CharField(_(u'Subjects'), max_length=150, blank=True,
        help_text=_(u'Separate two or more subjects with a comma.'))
    can_login = models.BooleanField(_(u'Can Login'), default=True)
    external = models.BooleanField(_(u'External'), default=False)
    barcode = models.CharField(max_length=100, editable=False, blank=True)
    _barcode = models.ImageField(upload_to='barcodes', editable=False,
        blank=True)
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

    def set_value(self, key, value=None, append=False):
        c = self.config()
        if append:
            if key in c:
                c[key].append(value)
            else:
                c[key] = [value]
        else:
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


RATING_CHOICES = (
    (u'A', _(u'A) useable')),
    (u'B', _(u'B) useable with restrictions')),
    (u'C', _(u'C) not useable')),
    (u'D', _(u'D) more ratings needed')),
)


class Company(CommonInfo):
    name = models.CharField(_(u'Name'), max_length=100)
    short_name = models.CharField(_(u'Short Name'), max_length=10, blank=True)
    fax = models.CharField(_(u'Fax'), max_length=30, blank=True)
    customer_number = models.CharField(_(u'Customer Number'), max_length=50,
        blank=True)
    web = models.URLField(_(u'Web'), blank=True)
    email = models.EmailField(_(u'Email'), blank=True)
    rate = models.BooleanField(_(u'Rate'), default=True)
    rating_users = models.ManyToManyField(User,
        verbose_name=_(u'Rating Users'), blank=True)
    rating = models.CharField(_(u'Rating'), max_length=1,
        choices=RATING_CHOICES, default=u'D')
    rating_note = models.TextField(_(u'Rating Note'), blank=True)

    def __unicode__(self):
        if self.short_name:
            return u'{0} ({1})'.format(self.name, self.short_name)
        return self.name

    def active_students(self):
        return self.students.filter(finished=False).count()

    def has_students(self):
        return bool(self.students.count())

    def calculate_rating(self):
        tmp = 0
        _all = []
        num = self.ratings.all().count()
        for r in self.ratings.all():
            tmp += r.average()
            _all.extend(r.as_list())
        try:
            rating = tmp / float(num)
        except ZeroDivisionError:
            return (u'D', 0.0)
        if rating >= 3 and min(_all) > 1:
            return (u'A', rating)
        elif rating < 2:
            return (u'C', rating)
        else:
            return (u'D', rating)

    class Meta:
        verbose_name = _(u'Company')
        verbose_name_plural = _(u'Companies')
        ordering = ('name',)


class CooperationContract(models.Model):
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='cooperations')
    date = models.DateField(_(u'Date'))
    job = models.CharField(_(u'Job'), max_length=50)
    full = models.BooleanField(_(u'Full-Cooperation'), default=True)
    active = models.BooleanField(_(u'Active'), default=True)
    note = models.TextField(_(u'Note'), blank=True)

    def __unicode__(self):
        return u'{0}, {1} ({2})'.format(self.company.name,
            self.date.strftime('%d.%m.%Y'), self.job)

    class Meta:
        verbose_name = _(u'Cooperation Contract')
        verbose_name_plural = _(u'Cooperation Contracts')


class Contact(models.Model):
    name_prefix = models.CharField(_(u'Name Prefix'), max_length=12)
    lastname = models.CharField(_(u'Lastname'), max_length=50)
    firstname = models.CharField(_(u'Firstname'), max_length=50)
    function = models.CharField(_(u'Function'), max_length=50, blank=True)
    phone = models.CharField(_(u'Phone'), max_length=30, blank=True)
    email = models.EmailField(_(u'Email'), blank=True)
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='contacts')

    audit_log = AuditLog()

    def __unicode__(self):
        s = u'{0} {1} {2}'.format(self.name_prefix, self.firstname,
                                  self.lastname)
        if self.function:
            return u'{0} ({1})'.format(s, self.function)
        return s

    def shortname(self):
        return u'{0} {1}'.format(self.name_prefix, self.lastname)

    class Meta:
        verbose_name = _(u'Contact')
        verbose_name_plural = _(u'Contacts')


class Note(models.Model):
    contact = models.ForeignKey(Contact, verbose_name=_(u'Contact'),
        related_name='notes')
    date = models.DateTimeField(_(u'Date'), auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    subject = models.CharField(_(u'Subject'), max_length=50)
    text = models.TextField(_(u'Text'))

    def __unicode__(self):
        return u'{0} - {1}, {2}, {3}'.format(self.contact, self.subject,
            self.user.get_profile(), self.date.strftime('%Y-%m-%d %H:%M'))

    class Meta:
        verbose_name = _(u'Note')
        verbose_name_plural = _(u'Notes')


class CompanyRating(models.Model):
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='ratings')
    user = models.ForeignKey(User, verbose_name=_(u'User'), null=True,
    blank=True)
    good_quality = models.PositiveSmallIntegerField(_(u'Good Quality'))
    delivery_time = models.PositiveSmallIntegerField(_(u'Delivery Time'))
    quality = models.PositiveSmallIntegerField(_(u'Quality'))
    price = models.PositiveSmallIntegerField(_(u'Price'))
    service = models.PositiveSmallIntegerField(_(u'Service'))
    attainability = models.PositiveSmallIntegerField(_(u'Attainability'))
    documentation = models.PositiveSmallIntegerField(_(u'Documentation'))
    rating = models.CharField(_(u'Rating'), max_length=1,
        choices=RATING_CHOICES)
    rated = models.DateTimeField(_(u'Rated'), auto_now_add=True)
    note = models.TextField(_(u'Note'), blank=True)

    def __unicode__(self):
        return u'{0} - {1} -> {2}'.format(self.user.get_profile(),
            self.company.name, self.rating)

    def as_list(self):
        return [self.good_quality, self.delivery_time, self.quality,
            self.price, self.service, self.attainability, self.documentation]

    def average(self):
        return sum(self.as_list()) / 7.0

    class Meta:
        verbose_name = _(u'Company Rating')
        verbose_name_plural = _(u'Company Ratings')
        permissions = (
            ('summarize', 'Summarize company ratings'),
        )


SUFFIX_CHOICES = ((u'a', u'a'), (u'b', u'b'), (u'c', u'c'), (u'd', u'd'))


class StudentGroup(models.Model):
    start_date = models.DateField(_(u'Start Date'))
    school_nr = models.CharField(_(u'School Number'), max_length=10,
        blank=True)
    job = models.CharField(_(u'Job'), max_length=50, blank=True)
    job_short = models.CharField(_(u'Job Short'), max_length=10,
        help_text=_(u'This field will be converted to uppercase.'))
    suffix = models.CharField(_(u'Suffix'), max_length=1, blank=True,
        choices=SUFFIX_CHOICES)

    @named(_(u'Groupname'))
    def name(self):
        return u'{0} {1}{2}'.format(self.job_short,
            self.start_date.strftime('%Y'), self.suffix)

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
SUIT_CHOICES = (
    (1, u'Die Berufseignung ist nicht gegeben.'),
    (2, u'Die Berufseignung ist bedingt gegeben.'),
    (3, u'Die Berufseignung ist gegeben.'),
)
EDU_CHOICES = (
    (1, u'Kein Abschluß'),
    (2, u'Hauptschule'),
    (3, u'MSA'),
    (4, u'Abitur'),
)


class Student(CommonInfo):
    lastname = models.CharField(_(u'Lastname'), max_length=50)
    firstname = models.CharField(_(u'Firstname'), max_length=50)
    sex = models.CharField(_(u'Sex'), max_length=1, choices=SEX_CHOICES)
    birthdate = models.DateField(_(u'Birthdate'))
    emergency = models.CharField(_(u'Notice in emergency'), max_length=100,
        blank=True)
    picture = models.ImageField(_(u'Picture'), upload_to='pictures',
        blank=True)
    email = models.EmailField(_(u'Email'), blank=True)
    mobile = models.CharField(_(u'Mobile'), max_length=30, blank=True)
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='students', blank=True, null=True)
    group = models.ForeignKey(StudentGroup, verbose_name=_(u'Group'),
        related_name='students', blank=True, null=True)
    cabinet = models.CharField(_(u'Cabinet'), max_length=20, blank=True)
    key = models.CharField(_(u'Key'), max_length=20, blank=True)
    school_education = models.PositiveSmallIntegerField(_(u'School Education'),
        choices=EDU_CHOICES, null=True, blank=True)
    applied_to = models.CharField(_(u'Applied to'), max_length=150,
        help_text=_(u'Separate two or more names with a comma.'), blank=True)
    forwarded_to = models.CharField(_(u'Forwarded to'), max_length=150,
        help_text=_(u'Separate two or more names with a comma.'), blank=True)
    jobs = models.CharField(_(u'Jobs'), max_length=150,
        help_text=_(u'Separate two or more jobs with a comma.'), blank=True)
    test_result = models.PositiveSmallIntegerField(_(u'Test Result'),
        blank=True, null=True)
    test_date = models.DateField(_(u'Test Date'), blank=True, null=True)
    suit_phrase = models.PositiveSmallIntegerField(_(u'Suit phrase'),
        choices=SUIT_CHOICES, blank=True, null=True)
    exam_1 = models.PositiveSmallIntegerField(_(u'Exam 1'), blank=True,
        null=True)
    exam_1_weight = models.PositiveSmallIntegerField(_(u'Exam 1 weight'),
        blank=True, null=True, default=30)
    exam_2 = models.PositiveSmallIntegerField(_(u'Exam 2'), blank=True,
        null=True)
    barcode = models.CharField(max_length=100, editable=False, blank=True)
    _barcode = models.ImageField(upload_to='barcodes', editable=False,
        blank=True)
    contract = models.ForeignKey(CooperationContract,
        verbose_name=_(u'Cooperation Contract'), related_name='students',
        null=True, blank=True)
    finished = models.BooleanField(_(u'Finished'), default=False)

    audit_log = AuditLog()

    def __unicode__(self):
        if self.group:
            return u'{0}, {1} ({2})'.format(self.lastname, self.firstname,
                                            self.group.name())
        else:
            return u'{0}, {1}'.format(self.lastname, self.firstname)

    def final_grade(self):
        if self.exam_1 and self.exam_2:
            weighted = self.exam_1 * self.exam_1_weight + \
                       self.exam_2 * (100 - self.exam_1_weight)
            return int(round(weighted / 100.0, 0))

    def first(self):
        return self.lastname[0].upper()

    def age(self):
        try:
            age = date.today() - self.birthdate
            return age.days // 365
        except:
            return 0

    class Meta:
        verbose_name = _(u'Student')
        verbose_name_plural = _(u'Students')
        ordering = ['company__name', 'lastname']


class PedagogicJournal(models.Model):
    group = models.OneToOneField(StudentGroup, verbose_name=_(u'Group'),
        related_name='journal')
    instructors = models.ManyToManyField(User, verbose_name=_(u'Instructors'),
        related_name='journals')
    created = models.DateField(_(u'Created'), auto_now_add=True)

    def __unicode__(self):
        return self.group.name()

    def is_writeable(self):
        return not self.group.finished()

    class Meta:
        verbose_name = _(u'Pedagogic Journal')
        verbose_name_plural = _(u'Pedagogic Journals')
        ordering = ['group__job_short']
        permissions = (
            ('read', u'Read all journals'),
        )


class JournalEntry(models.Model):
    journal = models.ForeignKey(PedagogicJournal, verbose_name=_(u'Journal'),
        related_name='entries')
    student = models.ForeignKey(Student, verbose_name=_(u'Student'),
        related_name='journal_entries')
    event = models.CharField(_(u'Event'), max_length=50, blank=True)
    text = models.TextField(_(u'Text'))
    created = models.DateTimeField(_(u'Created'), auto_now_add=True)
    created_by = models.ForeignKey(User, verbose_name=_(u'Created by'),
        related_name='journal_entries', editable=False, null=True,
        blank=True)
    last_edit = models.DateTimeField(_(u'Last edit'), auto_now=True)

    def __unicode__(self):
        if len(self.text) > 40:
            dots = u'...'
        else:
            dots = u''
        return u'[{0}] {1}{2}'.format(self.student, self.text[:40], dots)

    @named(_(u'Event'))
    def get_short_entry(self):
        if self.event:
            return self.event
        return self.text

    def has_media(self):
        return bool(self.media.all().count())

    class Meta:
        verbose_name = _(u'Journal Entry')
        verbose_name_plural = _(u'Journal Entries')
        ordering = ['journal__group__job', 'student__lastname', '-created']


MEDIA_TYPES_HTML = {
    'image': u'<img src="{0}" alt="{1}" width="800" />',
    'application': u'<a href="{0}">{1}</a>',
    'video': (u'<video src="{0}" width="320" height="200" controls preload>'
              u'{1}</video>'),
    'audio': u'<audio src="{0}" controls preload>{1}</audio>'
}


class JournalMedia(models.Model):
    entry = models.ForeignKey(JournalEntry, verbose_name=_(u'Journal Entry'),
        related_name='media')
    media_type = models.CharField(max_length=30, editable=False, blank=True)
    media = models.FileField(_(u'Media'), upload_to='journals/%Y')

    def __unicode__(self):
        return u'{0} ({1})'.format(self.media.name, self.media_type)

    def save(self, *args, **kwargs):
        type_ = guess_type(self.media.url, strict=False)[0]
        if type_ is None:
            self.media_type = u'application/octet-stream'
        else:
            self.media_type = type_
        super(JournalMedia, self).save(*args, **kwargs)

    def get_html_tag(self):
        for type_, tag in MEDIA_TYPES_HTML.iteritems():
            if self.media_type.startswith(type_):
                return mark_safe(tag.format(self.media.url, self.media.name))
        tag = MEDIA_TYPES_HTML['application']
        return mark_safe(tag.format(self.media.url, self.media.name))


PRESENCE_CHOICES = (
    (u'', u'leer'),
    (u'*', u'anwesend'),
    (u'T', u'nur telefonisch entschuldigt'),
    (u'|', u'fehlt unentschuldigt'),
    (u'K', u'krank (Nachweis vorhanden)'),
    (u'FT', u'Feiertag'),
    (u'B', u'Berufsschule anwesend'),
    (u'BK', u'keine Berufsschulkarte vorgelegt'),
    (u'BE', u'Berufsschule entschuldigt'),
    (u'F', u'Freistellung'),
    (u'Pr', u'Prüfung'),
    (u'U', u'Urlaub'),
    (u'/', u'nicht im bbz'),
    (u'P', u'Praktikum'),
    (u'BU', u'Bildungsurlaub'),
    (u'*F', u'anwesend freigestellt'),
)


class PresenceDay(models.Model):
    student = models.ForeignKey(Student, verbose_name=_(u'Student'),
        related_name='presence_days')
    date = models.DateField(_(u'Date'))
    entry = models.CharField(_(u'Entry'), max_length=2,
        choices=PRESENCE_CHOICES, default='', blank=True)
    lateness = models.IntegerField(_(u'Lateness'), default=0)
    excused = models.NullBooleanField(_(u'Excused'), blank=True)
    note = models.CharField(_(u'Note'), max_length=25, blank=True)
    instructor = models.ForeignKey(User, verbose_name=_(u'Instructor'),
        editable=False, null=True, blank=True)

    #audit_log = AuditLog()

    def __unicode__(self):
        return u'{0} {1} |{2}|'.format(self.student,
            self.date.strftime('%d.%m.%Y'), self.entry)

    class Meta:
        verbose_name = _(u'Presence')
        verbose_name_plural = _(u'Presences')
        ordering = ['student__lastname', '-date']


class PresencePrintout(models.Model):
    company = models.ForeignKey(Company, verbose_name=_(u'Company'),
        related_name='printouts')
    pdf = models.FileField(_(u'PDF-File'), upload_to='presence/%Y/%m')
    date = models.DateField(_(u'Date'))
    group = models.ForeignKey(StudentGroup, verbose_name=_(u'Group'),
        related_name='presence_printouts')
    generated = models.DateTimeField(_(u'Generated'), auto_now=True)

    def __unicode__(self):
        return u'{0} {1}'.format(self.company.short_name,
            self.date.strftime('%Y/%m'))

    class Meta:
        verbose_name = _(u'Printout')
        verbose_name_plural = _(u'Printouts')
        ordering = ['-date', 'company__name']


class PDFPrintout(models.Model):
    """Class for general printouts without any relations."""

    category = models.CharField(_(u'Category'), max_length=20)
    pdf = models.FileField(_(u'PDF-File'), upload_to='printouts/%Y/%m')
    generated = models.DateTimeField(_(u'Generated'), auto_now=True)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.category,
                                   self.generated.strftime('%Y/%m'))

    class Meta:
        verbose_name = _(u'General Printout')
        verbose_name_plural = _(u'General Printouts')
        ordering = ['-generated']


class InternalHelp(models.Model):
    title = models.CharField(_(u'Title'), max_length=50,
        help_text=_(u'Used for the title attribute of the help dialog.'))
    ident = models.SlugField(_(u'Identifier'),
        help_text=_(u'Help for the same topic in another language must '
                    u'define exactly the same identifier.'))
    lang = models.CharField(_(u'Language'), max_length=5,
        help_text=_(u'Lookup is done via istartswith.'))
    width = models.PositiveIntegerField(_(u'Dialog width'), default=500,
        help_text=_(u'Width of the help dialog.'))
    opener_class = models.CharField(_(u'Opener class'), max_length=15,
        default=u'.opener', help_text=_(u'CSS class of the element which '
            u'gets the click event to open the help dialog (jQuery notation).')
    )
    text = models.TextField(_(u'Text'), help_text=_(u'Main help text. You '
        u'can use HTML here.'))

    def __unicode__(self):
        return u'[{0}] {1} ({2})'.format(self.lang, self.title, self.ident)

    def save(self, *args, **kwargs):
        self.lang = self.lang.lower()
        super(InternalHelp, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u'Internal Help')
        verbose_name_plural = _(u'Internal Helps')
        ordering = ['ident', 'lang']
