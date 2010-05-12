
from south.db import db
from django.db import models
from loki.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'StatusParam'
        db.create_table('loki_statusparam', (
            ('id', orm['loki.StatusParam:id']),
            ('status', orm['loki.StatusParam:status']),
            ('type', orm['loki.StatusParam:type']),
            ('val', orm['loki.StatusParam:val']),
        ))
        db.send_create_signal('loki', ['StatusParam'])
        
        # Adding model 'ConfigParam'
        db.create_table('loki_configparam', (
            ('id', orm['loki.ConfigParam:id']),
            ('name', orm['loki.ConfigParam:name']),
            ('type', orm['loki.ConfigParam:type']),
            ('default', orm['loki.ConfigParam:default']),
            ('required', orm['loki.ConfigParam:required']),
        ))
        db.send_create_signal('loki', ['ConfigParam'])
        
        # Adding model 'StepParam'
        db.create_table('loki_stepparam', (
            ('id', orm['loki.StepParam:id']),
            ('step', orm['loki.StepParam:step']),
            ('type', orm['loki.StepParam:type']),
            ('val', orm['loki.StepParam:val']),
        ))
        db.send_create_signal('loki', ['StepParam'])
        
        # Adding model 'Step'
        db.create_table('loki_step', (
            ('id', orm['loki.Step:id']),
            ('slave', orm['loki.Step:slave']),
            ('type', orm['loki.Step:type']),
            ('num', orm['loki.Step:num']),
        ))
        db.send_create_signal('loki', ['Step'])
        
        # Adding model 'Config'
        db.create_table('loki_config', (
            ('id', orm['loki.Config:id']),
            ('name', orm['loki.Config:name']),
            ('module', orm['loki.Config:module']),
            ('content_type', orm['loki.Config:content_type']),
        ))
        db.send_create_signal('loki', ['Config'])
        
        # Adding model 'Scheduler'
        db.create_table('loki_scheduler', (
            ('id', orm['loki.Scheduler:id']),
            ('master', orm['loki.Scheduler:master']),
            ('type', orm['loki.Scheduler:type']),
        ))
        db.send_create_signal('loki', ['Scheduler'])
        
        # Adding model 'SchedulerParam'
        db.create_table('loki_schedulerparam', (
            ('id', orm['loki.SchedulerParam:id']),
            ('scheduler', orm['loki.SchedulerParam:scheduler']),
            ('type', orm['loki.SchedulerParam:type']),
            ('val', orm['loki.SchedulerParam:val']),
        ))
        db.send_create_signal('loki', ['SchedulerParam'])
        
        # Adding model 'Host'
        db.create_table('loki_host', (
            ('id', orm['loki.Host:id']),
            ('hostname', orm['loki.Host:hostname']),
        ))
        db.send_create_signal('loki', ['Host'])
        
        # Adding model 'Master'
        db.create_table('loki_master', (
            ('id', orm['loki.Master:id']),
            ('host', orm['loki.Master:host']),
            ('name', orm['loki.Master:name']),
            ('slave_port', orm['loki.Master:slave_port']),
            ('web_port', orm['loki.Master:web_port']),
        ))
        db.send_create_signal('loki', ['Master'])
        
        # Adding model 'Status'
        db.create_table('loki_status', (
            ('id', orm['loki.Status:id']),
            ('master', orm['loki.Status:master']),
            ('type', orm['loki.Status:type']),
        ))
        db.send_create_signal('loki', ['Status'])
        
        # Adding model 'Slave'
        db.create_table('loki_slave', (
            ('id', orm['loki.Slave:id']),
            ('host', orm['loki.Slave:host']),
            ('master', orm['loki.Slave:master']),
            ('name', orm['loki.Slave:name']),
            ('passwd', orm['loki.Slave:passwd']),
        ))
        db.send_create_signal('loki', ['Slave'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'StatusParam'
        db.delete_table('loki_statusparam')
        
        # Deleting model 'ConfigParam'
        db.delete_table('loki_configparam')
        
        # Deleting model 'StepParam'
        db.delete_table('loki_stepparam')
        
        # Deleting model 'Step'
        db.delete_table('loki_step')
        
        # Deleting model 'Config'
        db.delete_table('loki_config')
        
        # Deleting model 'Scheduler'
        db.delete_table('loki_scheduler')
        
        # Deleting model 'SchedulerParam'
        db.delete_table('loki_schedulerparam')
        
        # Deleting model 'Host'
        db.delete_table('loki_host')
        
        # Deleting model 'Master'
        db.delete_table('loki_master')
        
        # Deleting model 'Status'
        db.delete_table('loki_status')
        
        # Deleting model 'Slave'
        db.delete_table('loki_slave')
        
    
    
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
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
