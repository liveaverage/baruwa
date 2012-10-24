# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MailQueueItem'
        db.create_table(u'mailq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('messageid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('from_address', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('subject', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('hostname', self.gf('django.db.models.fields.TextField')()),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('attempts', self.gf('django.db.models.fields.IntegerField')()),
            ('lastattempt', self.gf('django.db.models.fields.DateTimeField')()),
            ('direction', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('reason', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('flag', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('status', ['MailQueueItem'])


    def backwards(self, orm):
        
        # Deleting model 'MailQueueItem'
        db.delete_table(u'mailq')


    models = {
        'status.mailqueueitem': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'MailQueueItem', 'db_table': "u'mailq'"},
            'attempts': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'flag': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'from_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastattempt': ('django.db.models.fields.DateTimeField', [], {}),
            'messageid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reason': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'subject': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['status']
