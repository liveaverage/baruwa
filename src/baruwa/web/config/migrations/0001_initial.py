# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Time'
        db.create_table('config_time', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('config', self.gf('django.db.models.fields.TextField')(default='#Example: weekly sunday')),
        ))
        db.send_create_signal('config', ['Time'])

        # Adding model 'Source'
        db.create_table('config_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('config', self.gf('django.db.models.fields.TextField')(default='#Example: user jjansens')),
        ))
        db.send_create_signal('config', ['Source'])

        # Adding model 'DestinationComponent'
        db.create_table('config_destinationcomponent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('domain', self.gf('baruwa.web.config.models.HostnameField')(max_length=255, blank=True)),
            ('regex', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('config', ['DestinationComponent'])

        # Adding unique constraint on 'DestinationComponent', fields ['destination_type', 'url', 'domain', 'regex']
        db.create_unique('config_destinationcomponent', ['destination_type', 'url', 'domain', 'regex'])

        # Adding M2M table for field destinations on 'DestinationComponent'
        db.create_table('config_destinationcomponent_destinations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('destinationcomponent', models.ForeignKey(orm['config.destinationcomponent'], null=False)),
            ('destination', models.ForeignKey(orm['config.destination'], null=False))
        ))
        db.create_unique('config_destinationcomponent_destinations', ['destinationcomponent_id', 'destination_id'])

        # Adding model 'Destination'
        db.create_table('config_destination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('is_local', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('config', ['Destination'])

        # Adding model 'DestinationPolicy'
        db.create_table('config_destinationpolicy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('permit_other_access', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('config', ['DestinationPolicy'])

        # Adding model 'OrderedDestination'
        db.create_table('config_ordereddestination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('destination_policy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.DestinationPolicy'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.Destination'])),
            ('permit', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('config', ['OrderedDestination'])

        # Adding unique constraint on 'OrderedDestination', fields ['destination_policy', 'destination', 'permit']
        db.create_unique('config_ordereddestination', ['destination_policy_id', 'destination_id', 'permit'])

        # Adding model 'AclRule'
        db.create_table('config_aclrule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.Time'])),
            ('time_invert', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.Source'])),
            ('destination_policy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['config.DestinationPolicy'])),
        ))
        db.send_create_signal('config', ['AclRule'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'OrderedDestination', fields ['destination_policy', 'destination', 'permit']
        db.delete_unique('config_ordereddestination', ['destination_policy_id', 'destination_id', 'permit'])

        # Removing unique constraint on 'DestinationComponent', fields ['destination_type', 'url', 'domain', 'regex']
        db.delete_unique('config_destinationcomponent', ['destination_type', 'url', 'domain', 'regex'])

        # Deleting model 'Time'
        db.delete_table('config_time')

        # Deleting model 'Source'
        db.delete_table('config_source')

        # Deleting model 'DestinationComponent'
        db.delete_table('config_destinationcomponent')

        # Removing M2M table for field destinations on 'DestinationComponent'
        db.delete_table('config_destinationcomponent_destinations')

        # Deleting model 'Destination'
        db.delete_table('config_destination')

        # Deleting model 'DestinationPolicy'
        db.delete_table('config_destinationpolicy')

        # Deleting model 'OrderedDestination'
        db.delete_table('config_ordereddestination')

        # Deleting model 'AclRule'
        db.delete_table('config_aclrule')


    models = {
        'config.aclrule': {
            'Meta': {'ordering': "['-order']", 'object_name': 'AclRule'},
            'destination_policy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.DestinationPolicy']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.Source']"}),
            'time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.Time']"}),
            'time_invert': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'config.destination': {
            'Meta': {'object_name': 'Destination'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_local': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'config.destinationcomponent': {
            'Meta': {'unique_together': "(('destination_type', 'url', 'domain', 'regex'),)", 'object_name': 'DestinationComponent'},
            'destination_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'destinations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['config.Destination']", 'symmetrical': 'False', 'blank': 'True'}),
            'domain': ('baruwa.web.config.models.HostnameField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'regex': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'config.destinationpolicy': {
            'Meta': {'object_name': 'DestinationPolicy'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'permit_other_access': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'config.ordereddestination': {
            'Meta': {'ordering': "['destination_policy', 'order']", 'unique_together': "(('destination_policy', 'destination', 'permit'),)", 'object_name': 'OrderedDestination'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.Destination']"}),
            'destination_policy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['config.DestinationPolicy']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'permit': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'config.source': {
            'Meta': {'object_name': 'Source'},
            'config': ('django.db.models.fields.TextField', [], {'default': "'#Example: user jjansens'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'config.time': {
            'Meta': {'object_name': 'Time'},
            'config': ('django.db.models.fields.TextField', [], {'default': "'#Example: weekly sunday'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['config']
