# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationDelegation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity', models.ForeignKey(verbose_name='Entity', to='entity.Entity')),
                ('moderator', models.ForeignKey(related_name='delegated moderator', verbose_name='Moderator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Moderation delegation',
                'verbose_name_plural': 'Moderation delegations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entity',
            name='diff_metadata',
            field=models.TextField(null=True, verbose_name='Diff pending review', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='moderators',
            field=models.ManyToManyField(related_name='moderation_delegated', verbose_name='Delegated Moderators', through='entity.ModerationDelegation', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='state',
            field=django_fsm.FSMField(default=b'new', protected=True, max_length=50, verbose_name='Entity Metadata State'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='temp_metadata',
            field=models.TextField(default=b'', null=True, verbose_name='Metadata pending review', blank=True),
            preserve_default=True,
        ),
    ]
