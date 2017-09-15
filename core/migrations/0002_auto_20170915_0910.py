# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accidententry',
            name='employee',
            field=models.ForeignKey(related_name='accidents', verbose_name='Verletzter Mitarbeiter', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='accidententry',
            name='place',
            field=models.ForeignKey(related_name='accident_entries', verbose_name='Place', to='core.Place'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='accidententry',
            name='student',
            field=models.ForeignKey(related_name='accidents', verbose_name='Verletzter Azubi', blank=True, to='core.Student', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='companyrating',
            name='company',
            field=models.ForeignKey(related_name='ratings', verbose_name='Company', to='core.Company'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='company',
            field=models.ForeignKey(related_name='contacts', verbose_name='Company', to='core.Company'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contactauditlogentry',
            name='action_user',
            field=audit_log.models.fields.LastUserField(related_name='_contact_audit_log_entry', editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contactauditlogentry',
            name='company',
            field=models.ForeignKey(related_name='_auditlog_contacts', verbose_name='Company', to='core.Company'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cooperationcontract',
            name='company',
            field=models.ForeignKey(related_name='cooperations', verbose_name='Company', to='core.Company'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='created_by',
            field=models.ForeignKey(related_name='journal_entries', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Created by'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='journal',
            field=models.ForeignKey(related_name='entries', verbose_name='Journal', to='core.PedagogicJournal'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='student',
            field=models.ForeignKey(related_name='journal_entries', verbose_name='Student', to='core.Student'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='journalmedia',
            name='entry',
            field=models.ForeignKey(related_name='media', verbose_name='Journal Entry', to='core.JournalEntry'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='note',
            name='contact',
            field=models.ForeignKey(related_name='notes', verbose_name='Contact', to='core.Contact'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pedagogicjournal',
            name='group',
            field=models.OneToOneField(related_name='journal', verbose_name='Group', to='core.StudentGroup'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pedagogicjournal',
            name='instructors',
            field=models.ManyToManyField(related_name='journals', verbose_name='Instructors', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='presenceday',
            name='student',
            field=models.ForeignKey(related_name='presence_days', verbose_name='Student', to='core.Student'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='presenceprintout',
            name='company',
            field=models.ForeignKey(related_name='printouts', verbose_name='Company', to='core.Company'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='presenceprintout',
            name='group',
            field=models.ForeignKey(related_name='presence_printouts', verbose_name='Group', to='core.StudentGroup'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='company',
            field=models.ForeignKey(related_name='students', verbose_name='Company', blank=True, to='core.Company', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='contract',
            field=models.ForeignKey(related_name='students', verbose_name='Cooperation Contract', blank=True, to='core.CooperationContract', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='group',
            field=models.ForeignKey(related_name='students', verbose_name='Group', blank=True, to='core.StudentGroup', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='action_user',
            field=audit_log.models.fields.LastUserField(related_name='_student_audit_log_entry', editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='company',
            field=models.ForeignKey(related_name='_auditlog_students', verbose_name='Company', blank=True, to='core.Company', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='contract',
            field=models.ForeignKey(related_name='_auditlog_students', verbose_name='Cooperation Contract', blank=True, to='core.CooperationContract', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentauditlogentry',
            name='group',
            field=models.ForeignKey(related_name='_auditlog_students', verbose_name='Group', blank=True, to='core.StudentGroup', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentgroup',
            name='suffix',
            field=models.CharField(blank=True, max_length=1, verbose_name='Suffix', choices=[('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd'), ('e', 'e'), ('f', 'f'), ('s', 's'), ('u', 'u')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='part',
            field=models.ForeignKey(related_name='profiles', verbose_name='Part', blank=True, to='core.Part', null=True),
            preserve_default=True,
        ),
    ]
