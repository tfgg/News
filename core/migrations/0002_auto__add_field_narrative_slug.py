# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Narrative.slug'
        db.add_column('core_narrative', 'slug', self.gf('django.db.models.fields.SlugField')(default='placeholder', max_length=50, db_index=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Narrative.slug'
        db.delete_column('core_narrative', 'slug')


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
            'slug': ('django.db.models.fields.SlugField', [], {'default': "'placeholder'", 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']
