# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MailHost'
        db.create_table('mail_hosts', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=25)),
            ('useraddress', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mh_ua', to=orm['accounts.UserAddresses'])),
        ))
        db.send_create_signal('config', ['MailHost'])

        # Adding model 'MailAuthHost'
        db.create_table('auth_hosts', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('protocol', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('port', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('split_address', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('useraddress', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mah_ua', to=orm['accounts.UserAddresses'])),
        ))
        db.send_create_signal('config', ['MailAuthHost'])

        # Adding model 'ScannerHost'
        db.create_table('scanners', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('config', ['ScannerHost'])

        # Adding model 'ConfigSection'
        db.create_table('scanner_config_sections', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('config', ['ConfigSection'])

        # Adding model 'ScannerConfig'
        db.create_table('scanner_config', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('internal', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('external', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('display', self.gf('django.db.models.fields.TextField')()),
            ('help', self.gf('django.db.models.fields.TextField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.ConfigSection'])),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.ScannerHost'])),
        ))
        db.send_create_signal('config', ['ScannerConfig'])


    def backwards(self, orm):
        
        # Deleting model 'MailHost'
        db.delete_table('mail_hosts')

        # Deleting model 'MailAuthHost'
        db.delete_table('auth_hosts')

        # Deleting model 'ScannerHost'
        db.delete_table('scanners')

        # Deleting model 'ConfigSection'
        db.delete_table('scanner_config_sections')

        # Deleting model 'ScannerConfig'
        db.delete_table('scanner_config')


    models = {
        'accounts.useraddresses': {
            'Meta': {'object_name': 'UserAddresses', 'db_table': "'user_addresses'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'address_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load_balance': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'config.configsection': {
            'Meta': {'object_name': 'ConfigSection', 'db_table': "'scanner_config_sections'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'config.mailauthhost': {
            'Meta': {'object_name': 'MailAuthHost', 'db_table': "'auth_hosts'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'protocol': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'split_address': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'useraddress': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mah_ua'", 'to': "orm['accounts.UserAddresses']"})
        },
        'config.mailhost': {
            'Meta': {'object_name': 'MailHost', 'db_table': "'mail_hosts'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'useraddress': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mh_ua'", 'to': "orm['accounts.UserAddresses']"})
        },
        'config.scannerconfig': {
            'Meta': {'object_name': 'ScannerConfig', 'db_table': "'scanner_config'"},
            'display': ('django.db.models.fields.TextField', [], {}),
            'external': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'help': ('django.db.models.fields.TextField', [], {}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.ScannerHost']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.ConfigSection']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'config.scannerhost': {
            'Meta': {'object_name': 'ScannerHost', 'db_table': "'scanners'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['config']
