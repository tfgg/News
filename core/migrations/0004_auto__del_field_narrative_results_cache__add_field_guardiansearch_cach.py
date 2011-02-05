# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Narrative.results_cache'
        db.delete_column('core_narrative', 'results_cache')

        # Adding field 'GuardianSearch.cache'
        db.add_column('core_guardiansearch', 'cache', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Narrative.results_cache'
        db.add_column('core_narrative', 'results_cache', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Deleting field 'GuardianSearch.cache'
        db.delete_column('core_guardiansearch', 'cache')


    models = {
        'core.guardiansearch': {
            'Meta': {'object_name': 'GuardianSearch'},
            'cache': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narrative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Narrative']"}),
            'tags': ('django.db.models.fields.TextField', [], {}),
            'term': ('django.db.models.fields.TextField', [], {})
        },
        'core.narrative': {
            'Meta': {'object_name': 'Narrative'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']
