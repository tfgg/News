# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Narrative'
        db.create_table('core_narrative', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Narrative'])

        # Adding model 'GuardianSearch'
        db.create_table('core_guardiansearch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('narrative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Narrative'])),
            ('term', self.gf('django.db.models.fields.TextField')()),
            ('tags', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['GuardianSearch'])


    def backwards(self, orm):
        
        # Deleting model 'Narrative'
        db.delete_table('core_narrative')

        # Deleting model 'GuardianSearch'
        db.delete_table('core_guardiansearch')


    models = {
        'core.guardiansearch': {
            'Meta': {'object_name': 'GuardianSearch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narrative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Narrative']"}),
            'tags': ('django.db.models.fields.TextField', [], {}),
            'term': ('django.db.models.fields.TextField', [], {})
        },
        'core.narrative': {
            'Meta': {'object_name': 'Narrative'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']
