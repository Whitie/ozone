# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Part'
        db.create_table(u'core_part', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'core', ['Part'])

        # Adding model 'UserProfile'
        db.create_table(u'core_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('name_prefix', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('birthdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='profiles', null=True, to=orm['core.Part'])),
            ('subjects', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('can_login', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('_barcode', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('_config', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'core', ['UserProfile'])

        # Adding model 'News'
        db.create_table(u'core_news', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'core', ['News'])

        # Adding model 'Company'
        db.create_table(u'core_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('customer_number', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('web', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('rate', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('rating', self.gf('django.db.models.fields.CharField')(default=u'D', max_length=1)),
            ('rating_note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'core', ['Company'])

        # Adding M2M table for field rating_users on 'Company'
        m2m_table_name = db.shorten_name(u'core_company_rating_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('company', models.ForeignKey(orm[u'core.company'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['company_id', 'user_id'])

        # Adding model 'CooperationContract'
        db.create_table(u'core_cooperationcontract', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cooperations', to=orm['core.Company'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('job', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('full', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'core', ['CooperationContract'])

        # Adding model 'ContactAuditLogEntry'
        db.create_table(u'core_contactauditlogentry', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name_prefix', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_contacts', to=orm['core.Company'])),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_contact_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'core', ['ContactAuditLogEntry'])

        # Adding model 'Contact'
        db.create_table(u'core_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name_prefix', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contacts', to=orm['core.Company'])),
        ))
        db.send_create_signal(u'core', ['Contact'])

        # Adding model 'Note'
        db.create_table(u'core_note', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notes', to=orm['core.Contact'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'core', ['Note'])

        # Adding model 'CompanyRating'
        db.create_table(u'core_companyrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ratings', to=orm['core.Company'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('good_quality', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('delivery_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('quality', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('price', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('service', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('attainability', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('documentation', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('rated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'core', ['CompanyRating'])

        # Adding model 'StudentGroup'
        db.create_table(u'core_studentgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('school_nr', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('job', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('job_short', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
        ))
        db.send_create_signal(u'core', ['StudentGroup'])

        # Adding model 'StudentAuditLogEntry'
        db.create_table(u'core_studentauditlogentry', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('birthdate', self.gf('django.db.models.fields.DateField')()),
            ('emergency', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_students', null=True, to=orm['core.Company'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_students', null=True, to=orm['core.StudentGroup'])),
            ('cabinet', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('school_education', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('applied_to', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('forwarded_to', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('jobs', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('test_result', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('test_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('suit_phrase', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('exam_1', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('exam_1_weight', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=30, null=True, blank=True)),
            ('exam_2', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('_barcode', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('contract', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_students', null=True, to=orm['core.CooperationContract'])),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_student_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'core', ['StudentAuditLogEntry'])

        # Adding model 'Student'
        db.create_table(u'core_student', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('birthdate', self.gf('django.db.models.fields.DateField')()),
            ('emergency', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='students', null=True, to=orm['core.Company'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='students', null=True, to=orm['core.StudentGroup'])),
            ('cabinet', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('school_education', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('applied_to', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('forwarded_to', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('jobs', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('test_result', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('test_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('suit_phrase', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('exam_1', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('exam_1_weight', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=30, null=True, blank=True)),
            ('exam_2', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('_barcode', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('contract', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='students', null=True, to=orm['core.CooperationContract'])),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['Student'])

        # Adding model 'PedagogicJournal'
        db.create_table(u'core_pedagogicjournal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.OneToOneField')(related_name='journal', unique=True, to=orm['core.StudentGroup'])),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['PedagogicJournal'])

        # Adding M2M table for field instructors on 'PedagogicJournal'
        m2m_table_name = db.shorten_name(u'core_pedagogicjournal_instructors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pedagogicjournal', models.ForeignKey(orm[u'core.pedagogicjournal'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pedagogicjournal_id', 'user_id'])

        # Adding model 'JournalEntry'
        db.create_table(u'core_journalentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('journal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['core.PedagogicJournal'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='journal_entries', to=orm['core.Student'])),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='journal_entries', null=True, to=orm['auth.User'])),
            ('last_edit', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['JournalEntry'])

        # Adding model 'JournalMedia'
        db.create_table(u'core_journalmedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='media', to=orm['core.JournalEntry'])),
            ('media_type', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('media', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'core', ['JournalMedia'])

        # Adding model 'PresenceDay'
        db.create_table(u'core_presenceday', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='presence_days', to=orm['core.Student'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('entry', self.gf('django.db.models.fields.CharField')(default='', max_length=2, blank=True)),
            ('lateness', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('excused', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('instructor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['PresenceDay'])

        # Adding model 'PresencePrintout'
        db.create_table(u'core_presenceprintout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='printouts', to=orm['core.Company'])),
            ('pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='presence_printouts', to=orm['core.StudentGroup'])),
            ('generated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['PresencePrintout'])

        # Adding model 'PDFPrintout'
        db.create_table(u'core_pdfprintout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('generated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['PDFPrintout'])

        # Adding model 'InternalHelp'
        db.create_table(u'core_internalhelp', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ident', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=500)),
            ('opener_class', self.gf('django.db.models.fields.CharField')(default=u'.opener', max_length=15)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'core', ['InternalHelp'])


    def backwards(self, orm):
        # Deleting model 'Part'
        db.delete_table(u'core_part')

        # Deleting model 'UserProfile'
        db.delete_table(u'core_userprofile')

        # Deleting model 'News'
        db.delete_table(u'core_news')

        # Deleting model 'Company'
        db.delete_table(u'core_company')

        # Removing M2M table for field rating_users on 'Company'
        db.delete_table(db.shorten_name(u'core_company_rating_users'))

        # Deleting model 'CooperationContract'
        db.delete_table(u'core_cooperationcontract')

        # Deleting model 'ContactAuditLogEntry'
        db.delete_table(u'core_contactauditlogentry')

        # Deleting model 'Contact'
        db.delete_table(u'core_contact')

        # Deleting model 'Note'
        db.delete_table(u'core_note')

        # Deleting model 'CompanyRating'
        db.delete_table(u'core_companyrating')

        # Deleting model 'StudentGroup'
        db.delete_table(u'core_studentgroup')

        # Deleting model 'StudentAuditLogEntry'
        db.delete_table(u'core_studentauditlogentry')

        # Deleting model 'Student'
        db.delete_table(u'core_student')

        # Deleting model 'PedagogicJournal'
        db.delete_table(u'core_pedagogicjournal')

        # Removing M2M table for field instructors on 'PedagogicJournal'
        db.delete_table(db.shorten_name(u'core_pedagogicjournal_instructors'))

        # Deleting model 'JournalEntry'
        db.delete_table(u'core_journalentry')

        # Deleting model 'JournalMedia'
        db.delete_table(u'core_journalmedia')

        # Deleting model 'PresenceDay'
        db.delete_table(u'core_presenceday')

        # Deleting model 'PresencePrintout'
        db.delete_table(u'core_presenceprintout')

        # Deleting model 'PDFPrintout'
        db.delete_table(u'core_pdfprintout')

        # Deleting model 'InternalHelp'
        db.delete_table(u'core_internalhelp')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.company': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Company'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'customer_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'rate': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rating': ('django.db.models.fields.CharField', [], {'default': "u'D'", 'max_length': '1'}),
            'rating_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rating_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'web': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'core.companyrating': {
            'Meta': {'object_name': 'CompanyRating'},
            'attainability': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['core.Company']"}),
            'delivery_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'documentation': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'good_quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'rated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'service': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'core.contact': {
            'Meta': {'object_name': 'Contact'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': u"orm['core.Company']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name_prefix': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'core.contactauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'ContactAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_contact_audit_log_entry'"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_contacts'", 'to': u"orm['core.Company']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name_prefix': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'core.cooperationcontract': {
            'Meta': {'object_name': 'CooperationContract'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cooperations'", 'to': u"orm['core.Company']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'full': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'core.internalhelp': {
            'Meta': {'ordering': "['ident', 'lang']", 'object_name': 'InternalHelp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'opener_class': ('django.db.models.fields.CharField', [], {'default': "u'.opener'", 'max_length': '15'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '500'})
        },
        u'core.journalentry': {
            'Meta': {'ordering': "['journal__group__job', 'student__lastname', '-created']", 'object_name': 'JournalEntry'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'journal_entries'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['core.PedagogicJournal']"}),
            'last_edit': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'journal_entries'", 'to': u"orm['core.Student']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'core.journalmedia': {
            'Meta': {'object_name': 'JournalMedia'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'media'", 'to': u"orm['core.JournalEntry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'core.news': {
            'Meta': {'ordering': "('-date', 'author')", 'object_name': 'News'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'core.note': {
            'Meta': {'object_name': 'Note'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': u"orm['core.Contact']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'core.part': {
            'Meta': {'object_name': 'Part'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'core.pdfprintout': {
            'Meta': {'ordering': "['-generated']", 'object_name': 'PDFPrintout'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'generated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        u'core.pedagogicjournal': {
            'Meta': {'ordering': "['group__job_short']", 'object_name': 'PedagogicJournal'},
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'journal'", 'unique': 'True', 'to': u"orm['core.StudentGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'journals'", 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        },
        u'core.presenceday': {
            'Meta': {'ordering': "['student__lastname', '-date']", 'object_name': 'PresenceDay'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'entry': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2', 'blank': 'True'}),
            'excused': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'lateness': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presence_days'", 'to': u"orm['core.Student']"})
        },
        u'core.presenceprintout': {
            'Meta': {'ordering': "['-date', 'company__name']", 'object_name': 'PresencePrintout'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'printouts'", 'to': u"orm['core.Company']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'generated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presence_printouts'", 'to': u"orm['core.StudentGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        u'core.student': {
            'Meta': {'ordering': "['company__name', 'lastname']", 'object_name': 'Student'},
            '_barcode': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'applied_to': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {}),
            'cabinet': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'students'", 'null': 'True', 'to': u"orm['core.Company']"}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'students'", 'null': 'True', 'to': u"orm['core.CooperationContract']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'emergency': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'exam_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exam_1_weight': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '30', 'null': 'True', 'blank': 'True'}),
            'exam_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'forwarded_to': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'students'", 'null': 'True', 'to': u"orm['core.StudentGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobs': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'school_education': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'suit_phrase': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'test_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'test_result': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'core.studentauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'StudentAuditLogEntry'},
            '_barcode': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_student_audit_log_entry'"}),
            'applied_to': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {}),
            'cabinet': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_students'", 'null': 'True', 'to': u"orm['core.Company']"}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_students'", 'null': 'True', 'to': u"orm['core.CooperationContract']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'emergency': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'exam_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exam_1_weight': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '30', 'null': 'True', 'blank': 'True'}),
            'exam_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'forwarded_to': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_students'", 'null': 'True', 'to': u"orm['core.StudentGroup']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'jobs': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'school_education': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'suit_phrase': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'test_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'test_result': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'core.studentgroup': {
            'Meta': {'ordering': "['-start_date', 'job']", 'object_name': 'StudentGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'job_short': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'school_nr': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        u'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            '_barcode': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            '_config': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'can_login': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'name_prefix': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'profiles'", 'null': 'True', 'to': u"orm['core.Part']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'subjects': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        }
    }

    complete_apps = ['core']