# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Step.slave'
        db.delete_column('loki_step', 'slave_id')


    def backwards(self, orm):
        
        # Adding field 'Step.slave'
        db.add_column('loki_step', 'slave', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='steps', to=orm['loki.Slave']), keep_default=False)


    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'loki.builder': {
            'Meta': {'object_name': 'Builder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'builders'", 'to': "orm['loki.Master']"}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '25', 'db_index': 'True'}),
            'slaves': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'builders'", 'symmetrical': 'False', 'to': "orm['loki.Slave']"})
        },
        'loki.config': {
            'Meta': {'object_name': 'Config'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'loki.configparam': {
            'Meta': {'object_name': 'ConfigParam'},
            'default': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Config']"})
        },
        'loki.host': {
            'Meta': {'object_name': 'Host'},
            'base_dir': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'loki.master': {
            'Meta': {'object_name': 'Master'},
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'masters'", 'to': "orm['loki.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '25', 'db_index': 'True'}),
            'slave_port': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'web_port': ('django.db.models.fields.IntegerField', [], {'max_length': '5'})
        },
        'loki.scheduler': {
            'Meta': {'object_name': 'Scheduler'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schedulers'", 'to': "orm['loki.Master']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduler_type'", 'to': "orm['loki.Config']"})
        },
        'loki.schedulerparam': {
            'Meta': {'object_name': 'SchedulerParam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scheduler': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Scheduler']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['loki.ConfigParam']"}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'loki.slave': {
            'Meta': {'object_name': 'Slave'},
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slaves'", 'to': "orm['loki.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slaves'", 'to': "orm['loki.Master']"}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '25', 'db_index': 'True'}),
            'passwd': ('django.db.models.fields.SlugField', [], {'max_length': '25', 'db_index': 'True'})
        },
        'loki.status': {
            'Meta': {'object_name': 'Status'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status'", 'to': "orm['loki.Master']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_type'", 'to': "orm['loki.Config']"})
        },
        'loki.statusparam': {
            'Meta': {'object_name': 'StatusParam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Status']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['loki.ConfigParam']"}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'loki.step': {
            'Meta': {'object_name': 'Step'},
            'builder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['loki.Builder']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'step_type'", 'to': "orm['loki.Config']"})
        },
        'loki.stepparam': {
            'Meta': {'object_name': 'StepParam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'step': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Step']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['loki.ConfigParam']"}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['loki']
