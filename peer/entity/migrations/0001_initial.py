# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import vff.git_backend
import datetime
from django.conf import settings
import vff.field
import vff.storage
import peer.customfields


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metadata', vff.field.VersionedFileField(storage=vff.storage.VersionedStorage(vff.git_backend.GitBackend, None), null=True, verbose_name='Entity metadata', blank=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('modification_time', models.DateTimeField(auto_now=True, verbose_name='Modification time')),
                ('metarefresh_frequency', models.CharField(default=b'N', max_length=1, verbose_name='Metadata refreshing frequency', db_index=True, choices=[(b'N', b'Never'), (b'D', b'Daily'), (b'W', b'Weekly'), (b'M', b'Monthly')])),
                ('metarefresh_last_run', models.DateTimeField(auto_now_add=True, verbose_name='Last time refreshed')),
            ],
            options={
                'ordering': ('-creation_time',),
                'verbose_name': 'Entity',
                'verbose_name_plural': 'Entities',
                'permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', peer.customfields.SafeCharField(max_length=200, verbose_name='Name of the group')),
                ('query', peer.customfields.SafeCharField(max_length=100, verbose_name='Query that defines the group')),
                ('owner', models.ForeignKey(verbose_name='Owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Entity group',
                'verbose_name_plural': 'Entity groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PermissionDelegation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Delegation date')),
                ('delegate', models.ForeignKey(related_name='permission_delegate', verbose_name='Delegate', to=settings.AUTH_USER_MODEL)),
                ('entity', models.ForeignKey(verbose_name='Entity', to='entity.Entity')),
            ],
            options={
                'verbose_name': 'Permission delegation',
                'verbose_name_plural': 'Permission delegations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entity',
            name='delegates',
            field=models.ManyToManyField(related_name='permission_delegated', verbose_name='Delegates', through='entity.PermissionDelegation', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='domain',
            field=models.ForeignKey(verbose_name='Domain', to='domain.Domain'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='owner',
            field=models.ForeignKey(verbose_name='Owner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='subscribers',
            field=models.ManyToManyField(related_name='monitor_entities', verbose_name='Subscribers', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
