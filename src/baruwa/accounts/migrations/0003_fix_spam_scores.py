# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserProfile.sa_high_score'
        db.alter_column('profiles', 'sa_high_score', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'UserProfile.sa_low_score'
        db.alter_column('profiles', 'sa_low_score', self.gf('django.db.models.fields.FloatField')())


    def backwards(self, orm):

        # Changing field 'UserProfile.sa_high_score'
        db.alter_column('profiles', 'sa_high_score', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'UserProfile.sa_low_score'
        db.alter_column('profiles', 'sa_low_score', self.gf('django.db.models.fields.IntegerField')())


    models = {}

    complete_apps = ['accounts']