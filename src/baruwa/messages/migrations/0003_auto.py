# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Message', fields ['timestamp']
        db.create_index('messages', ['timestamp'])

        # Adding index on 'Archive', fields ['timestamp']
        db.create_index(u'archive', ['timestamp'])


    def backwards(self, orm):
        
        # Removing index on 'Archive', fields ['timestamp']
        db.delete_index(u'archive', ['timestamp'])

        # Removing index on 'Message', fields ['timestamp']
        db.delete_index('messages', ['timestamp'])


    models = {
        'messages.archive': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Archive', 'db_table': "u'archive'"},
            'actions': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'blacklisted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'clientip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'from_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'from_domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'headers': ('django.db.models.fields.TextField', [], {}),
            'highspam': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'hostname': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'isquarantined': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'nameinfected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'otherinfected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rblspam': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sascore': ('django.db.models.fields.FloatField', [], {}),
            'saspam': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scaned': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'size': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'spam': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'spamreport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'to_domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'virusinfected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'whitelisted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        'messages.message': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Message', 'db_table': "'messages'"},
            'actions': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'blacklisted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'clientip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'from_address': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'from_domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'headers': ('django.db.models.fields.TextField', [], {}),
            'highspam': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'hostname': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'isquarantined': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'nameinfected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'otherinfected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rblspam': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sascore': ('django.db.models.fields.FloatField', [], {}),
            'saspam': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scaned': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'spam': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'spamreport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'to_domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'virusinfected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'whitelisted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        'messages.messagestats': {
            'Meta': {'object_name': 'MessageStats', 'managed': 'False'},
            'clean_mail': ('django.db.models.fields.IntegerField', [], {}),
            'high_spam': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infected': ('django.db.models.fields.IntegerField', [], {}),
            'otherinfected': ('django.db.models.fields.IntegerField', [], {}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'spam_mail': ('django.db.models.fields.IntegerField', [], {}),
            'total': ('django.db.models.fields.IntegerField', [], {}),
            'virii': ('django.db.models.fields.IntegerField', [], {})
        },
        'messages.messagetotals': {
            'Meta': {'object_name': 'MessageTotals', 'managed': 'False'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_total': ('django.db.models.fields.IntegerField', [], {}),
            'size_total': ('django.db.models.fields.IntegerField', [], {}),
            'spam_percent': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'spam_total': ('django.db.models.fields.IntegerField', [], {}),
            'virus_percent': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'virus_total': ('django.db.models.fields.IntegerField', [], {})
        },
        'messages.recipient': {
            'Meta': {'object_name': 'Recipient', 'db_table': "u'message_recipients'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['messages.Message']"}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'to_domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'messages.release': {
            'Meta': {'object_name': 'Release', 'db_table': "u'quarantine_releases'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'released': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'messages.sarules': {
            'Meta': {'object_name': 'SaRules', 'db_table': "u'sa_rules'"},
            'rule': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'rule_desc': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'messages.spamscores': {
            'Meta': {'object_name': 'SpamScores', 'managed': 'False'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['messages']
