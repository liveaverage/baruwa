# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'MailQueueItem', fields ['direction']
        db.create_index(u'mailq', ['direction'])


    def backwards(self, orm):
        
        # Removing index on 'MailQueueItem', fields ['direction']
        db.delete_index(u'mailq', ['direction'])


    models = {
        'status.mailqueueitem': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'MailQueueItem', 'db_table': "u'mailq'"},
            'attempts': ('django.db.models.fields.IntegerField', [], {}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
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
