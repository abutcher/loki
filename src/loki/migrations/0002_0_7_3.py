
from south.db import db
from django.db import models
from loki.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Host.password'
        db.add_column('loki_host', 'password', orm['loki.host:password'])
        
        # Adding field 'Host.username'
        db.add_column('loki_host', 'username', orm['loki.host:username'])
        
        # Adding field 'Host.base_dir'
        db.add_column('loki_host', 'base_dir', orm['loki.host:base_dir'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Host.password'
        db.delete_column('loki_host', 'password')
        
        # Deleting field 'Host.username'
        db.delete_column('loki_host', 'username')
        
        # Deleting field 'Host.base_dir'
        db.delete_column('loki_host', 'base_dir')
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'loki.config': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'loki.configparam': {
            'default': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Config']"})
        },
        'loki.host': {
            'base_dir': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'loki.master': {
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'masters'", 'to': "orm['loki.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '25', 'db_index': 'True'}),
            'slave_port': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'web_port': ('django.db.models.fields.IntegerField', [], {'max_length': '5'})
        },
        'loki.scheduler': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schedulers'", 'to': "orm['loki.Master']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduler_type'", 'to': "orm['loki.Config']"})
        },
        'loki.schedulerparam': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scheduler': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Scheduler']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['loki.ConfigParam']"}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'loki.slave': {
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slaves'", 'to': "orm['loki.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slaves'", 'to': "orm['loki.Master']"}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '25', 'db_index': 'True'}),
            'passwd': ('django.db.models.fields.SlugField', [], {'max_length': '25', 'db_index': 'True'})
        },
        'loki.status': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status'", 'to': "orm['loki.Master']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_type'", 'to': "orm['loki.Config']"})
        },
        'loki.statusparam': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Status']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['loki.ConfigParam']"}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'loki.step': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'slave': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['loki.Slave']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'step_type'", 'to': "orm['loki.Config']"})
        },
        'loki.stepparam': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'step': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': "orm['loki.Step']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['loki.ConfigParam']"}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['loki']
