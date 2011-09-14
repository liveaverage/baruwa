# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Message'
        db.create_table('messages', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('actions', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('clientip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('from_address', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('from_domain', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('headers', self.gf('django.db.models.fields.TextField')()),
            ('hostname', self.gf('django.db.models.fields.TextField')()),
            ('highspam', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('rblspam', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('saspam', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('spam', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('nameinfected', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('otherinfected', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('isquarantined', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('sascore', self.gf('django.db.models.fields.FloatField')()),
            ('scaned', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('blacklisted', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('spamreport', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('whitelisted', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('subject', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('to_domain', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('virusinfected', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('messages', ['Message'])

        # Adding model 'Recipient'
        db.create_table(u'message_recipients', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['messages.Message'])),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('to_domain', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('messages', ['Recipient'])

        # Adding model 'SaRules'
        db.create_table(u'sa_rules', (
            ('rule', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('rule_desc', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('messages', ['SaRules'])

        # Adding model 'Release'
        db.create_table(u'quarantine_releases', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('released', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('messages', ['Release'])

        # Adding model 'Archive'
        db.create_table(u'archive', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('actions', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('clientip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('from_address', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('from_domain', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('headers', self.gf('django.db.models.fields.TextField')()),
            ('hostname', self.gf('django.db.models.fields.TextField')()),
            ('highspam', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('rblspam', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('saspam', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('spam', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('nameinfected', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('otherinfected', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('isquarantined', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('sascore', self.gf('django.db.models.fields.FloatField')()),
            ('scaned', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('size', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('blacklisted', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('spamreport', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('whitelisted', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('subject', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('to_domain', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('virusinfected', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('messages', ['Archive'])


    def backwards(self, orm):
        
        # Deleting model 'Message'
        db.delete_table('messages')

        # Deleting model 'Recipient'
        db.delete_table(u'message_recipients')

        # Deleting model 'SaRules'
        db.delete_table(u'sa_rules')

        # Deleting model 'Release'
        db.delete_table(u'quarantine_releases')

        # Deleting model 'Archive'
        db.delete_table(u'archive')


    models = {
        'messages.archive': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Archive', 'db_table': "u'archive'"},
            'actions': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'blacklisted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'clientip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'date': ('django.db.models.fields.DateField', [], {}),
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
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
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
            'date': ('django.db.models.fields.DateField', [], {}),
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
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
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
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
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
