# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ModerationDelegation'
        db.create_table(u'entity_moderationdelegation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity.Entity'])),
            ('moderator', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'delegated moderator', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'entity', ['ModerationDelegation'])

        # Adding field 'Entity.state'
        db.add_column(u'entity_entity', 'state', self.gf('django_fsm.FSMField')(default='new', max_length=50), keep_default=False)

        # Adding field 'Entity.temp_metadata'
        db.add_column(u'entity_entity', 'temp_metadata', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True), keep_default=False)

        # Adding field 'Entity.diff_metadata'
        db.add_column(u'entity_entity', 'diff_metadata', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'ModerationDelegation'
        db.delete_table(u'entity_moderationdelegation')

        # Deleting field 'Entity.state'
        db.delete_column(u'entity_entity', 'state')

        # Deleting field 'Entity.temp_metadata'
        db.delete_column(u'entity_entity', 'temp_metadata')

        # Deleting field 'Entity.diff_metadata'
        db.delete_column(u'entity_entity', 'diff_metadata')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 13, 13, 38, 56, 970625)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 13, 13, 38, 56, 970320)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'domain.domain': {
            'Meta': {'object_name': 'Domain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'moderator_team_domains'", 'symmetrical': 'False', 'through': u"orm['domain.DomainModeratorsTeamMembership']", 'to': u"orm['auth.User']"}),
            'name': ('peer.customfields.SafeCharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'team_domains'", 'symmetrical': 'False', 'through': u"orm['domain.DomainTeamMembership']", 'to': u"orm['auth.User']"}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'validation_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'domain.domainmoderatorsteammembership': {
            'Meta': {'object_name': 'DomainModeratorsTeamMembership'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['domain.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'domain_moderator_teams'", 'to': u"orm['auth.User']"})
        },
        u'domain.domainteammembership': {
            'Meta': {'object_name': 'DomainTeamMembership'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['domain.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'domain_teams'", 'to': u"orm['auth.User']"})
        },
        u'entity.entity': {
            'Meta': {'ordering': "('-creation_time',)", 'object_name': 'Entity'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'permission_delegated'", 'symmetrical': 'False', 'through': u"orm['entity.PermissionDelegation']", 'to': u"orm['auth.User']"}),
            'diff_metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['domain.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('vff.field.VersionedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'metarefresh_frequency': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1', 'db_index': 'True'}),
            'metarefresh_last_run': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'moderators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'moderation_delegated'", 'symmetrical': 'False', 'through': u"orm['entity.ModerationDelegation']", 'to': u"orm['auth.User']"}),
            'modification_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'state': ('django_fsm.FSMField', [], {'default': "'new'", 'max_length': '50'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'monitor_entities'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'temp_metadata': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        },
        u'entity.entitygroup': {
            'Meta': {'object_name': 'EntityGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('peer.customfields.SafeCharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'query': ('peer.customfields.SafeCharField', [], {'max_length': '100'})
        },
        u'entity.moderationdelegation': {
            'Meta': {'object_name': 'ModerationDelegation'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity.Entity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'delegated moderator'", 'to': u"orm['auth.User']"})
        },
        u'entity.permissiondelegation': {
            'Meta': {'object_name': 'PermissionDelegation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'delegate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_delegate'", 'to': u"orm['auth.User']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity.Entity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['entity']
