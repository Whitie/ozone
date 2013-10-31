# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OrderDay'
        db.create_table(u'orders_orderday', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('day', self.gf('django.db.models.fields.DateField')(unique=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'orders', ['OrderDay'])

        # Adding model 'Article'
        db.create_table(u'orders_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('supplier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Company'], null=True, blank=True)),
            ('ident', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('quantity', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'orders', ['Article'])

        # Adding model 'Cost'
        db.create_table(u'orders_cost', (
            ('ident', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'orders', ['Cost'])

        # Adding model 'OrderAuditLogEntry'
        db.create_table(u'orders_orderauditlogentry', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Article'])),
            ('memo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order_day', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_orders', to=orm['orders.OrderDay'])),
            ('for_test', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('for_repair', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'new', max_length=10)),
            ('ordered', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_order_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'orders', ['OrderAuditLogEntry'])

        # Adding model 'Order'
        db.create_table(u'orders_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Article'])),
            ('memo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order_day', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orders', to=orm['orders.OrderDay'])),
            ('for_test', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('for_repair', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'new', max_length=10)),
            ('ordered', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'orders', ['Order'])

        # Adding M2M table for field users on 'Order'
        m2m_table_name = db.shorten_name(u'orders_order_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('order', models.ForeignKey(orm[u'orders.order'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['order_id', 'user_id'])

        # Adding model 'DeliveredOrder'
        db.create_table(u'orders_deliveredorder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deliveries', to=orm['orders.Order'])),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'orders', ['DeliveredOrder'])

        # Adding model 'CostOrder'
        db.create_table(u'orders_costorder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cost', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Cost'])),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Order'])),
            ('percent', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'orders', ['CostOrder'])

        # Adding model 'Printout'
        db.create_table(u'orders_printout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_day', self.gf('django.db.models.fields.related.ForeignKey')(related_name='printouts', to=orm['orders.OrderDay'])),
            ('internal', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('generated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'orders', ['Printout'])


    def backwards(self, orm):
        # Deleting model 'OrderDay'
        db.delete_table(u'orders_orderday')

        # Deleting model 'Article'
        db.delete_table(u'orders_article')

        # Deleting model 'Cost'
        db.delete_table(u'orders_cost')

        # Deleting model 'OrderAuditLogEntry'
        db.delete_table(u'orders_orderauditlogentry')

        # Deleting model 'Order'
        db.delete_table(u'orders_order')

        # Removing M2M table for field users on 'Order'
        db.delete_table(db.shorten_name(u'orders_order_users'))

        # Deleting model 'DeliveredOrder'
        db.delete_table(u'orders_deliveredorder')

        # Deleting model 'CostOrder'
        db.delete_table(u'orders_costorder')

        # Deleting model 'Printout'
        db.delete_table(u'orders_printout')


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
        u'orders.article': {
            'Meta': {'object_name': 'Article'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Company']", 'null': 'True', 'blank': 'True'})
        },
        u'orders.cost': {
            'Meta': {'object_name': 'Cost'},
            'ident': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'orders.costorder': {
            'Meta': {'ordering': "['order']", 'object_name': 'CostOrder'},
            'cost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Cost']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"}),
            'percent': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'orders.deliveredorder': {
            'Meta': {'ordering': "['order', '-date']", 'object_name': 'DeliveredOrder'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deliveries'", 'to': u"orm['orders.Order']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'orders.order': {
            'Meta': {'object_name': 'Order'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Article']"}),
            'costs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['orders.Cost']", 'through': u"orm['orders.CostOrder']", 'symmetrical': 'False'}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'for_repair': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'for_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order_day': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders'", 'to': u"orm['orders.OrderDay']"}),
            'ordered': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '10'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        },
        u'orders.orderauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'OrderAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_order_audit_log_entry'"}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Article']"}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'for_repair': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'for_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'memo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order_day': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_orders'", 'to': u"orm['orders.OrderDay']"}),
            'ordered': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '10'})
        },
        u'orders.orderday': {
            'Meta': {'object_name': 'OrderDay'},
            'day': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'orders.printout': {
            'Meta': {'ordering': "['company_name', '-generated']", 'object_name': 'Printout'},
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'generated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'order_day': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'printouts'", 'to': u"orm['orders.OrderDay']"}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['orders']