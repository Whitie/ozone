# -*- coding: utf-8 -*-

import random
import uuid

from django.db import models
from django.contrib.auth.models import User

from ozone.core.models import StudentGroup
from ozone.feedback import utils

# Create your models here.

class Question(models.Model):
    text = models.CharField(u'Text')

    class Meta:
        verbose_name = u'Frage'
        verbose_name_plural = u'Fragen'


class QuestionSet(models.Model):
    name = models.CharField(u'Name', max_length=30)
    questions = models.ManyToManyField(Question, through='QuestionExtra',
                                       verbose_name=u'Fragen')

    class Meta:
        verbose_name = u'Fragenkatalog'
        verbose_name_plural = u'Fragenkataloge'


class QuestionExtra(models.Model):
    question = models.ForeignKey(Question, verbose_name=u'Frage')
    questionset = models.ForeignKey(QuestionSet, verbose_name=u'Fragenkatalog')
    position = models.PositiveSmallIntegerField(u'Position', default=1)
    num_text = models.CharField(u'Angezeigte Nummerierung', max_length=5,
                                blank=True)

    class Meta:
        verbose_name = u'Katalog -> Frage'
        verbose_name_plural = u'Katalog -> Fragen'


class Feedback(models.Model):
    group = models.ForeignKey(StudentGroup, verbose_name=u'Gruppe')
    course = models.CharField(u'Kurs', max_length=100)
    start_date = models.DateField(u'Datum Beginn')
    end_date = models.DateField(u'Datum Ende')
    instructor = models.ForeignKey(User, verbose_name=u'Ausbilder / Dozent')
    questionset = models.ForeignKey(QuestionSet, verbose_name=u'Fragenkatalog')
    hints = models.TextField(u'Hinweise', help_text=u'Dieser Text wird allen '
                             'Teilnehmern angezeigt.', blank=True)
    active = models.BooleanField(u'Aktiv', default=False)
    created = models.DateTimeField(u'Erstellt', auto_now_add=True)

    def __unicode__(self):
        return u'{0} - {1} ({2})'.format(unicode(self.group), self.course,
                                         self.instructor.get_full_name())

    def make_token(self):
        return utils.make_unique_token(unicode(self.group))

    class Meta:
        get_latest_by = 'created'
        ordering = '-created'
        verbose_name = u'Feedback'
        verbose_name_plural = u'Feedbacks'


STATE_CHOICES = (
    (u'n', u'Neu'),
    (u'u', u'In Bearbeitung'),
    (u'f', u'Beendet'),
)


class FeedbackToken(models.Model):
    feedback = models.ForeignKey(Feedback, verbose_name=u'Feedback')
    token = models.CharField(u'Token', max_length=10, unique=True)
    state = models.CharField(u'Status', max_length=1, choices=STATE_CHOICES,
                             default=u'n')

    def __unicode__(self):
        return self.token

    @property
    def in_use(self):
        return self.state == u'u'

    @property
    def finished(self):
        return self.state == u'f'

    class Meta:
        verbose_name = u'Token'
        verbose_name_plural = u'Tokens'


GRADE_CHOICES = ((x, unicode(x)) for x in range(1, 7))


class Answer(models.Model):
    feedback = models.ForeignKey(Feedback, verbose_name=u'Feedback')
    question = models.ForeignKey(Question, verbose_name=u'Frage')
    grade = models.PositiveSmallIntegerField(u'Note', choices=GRADE_CHOICES)
    notes = models.TextField(u'Bemerkungen', blank=True)

    class Meta:
        verbose_name = u'Antwort'
        verbose_name_plural = u'Antworten'
