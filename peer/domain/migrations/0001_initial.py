# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import peer.customfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', peer.customfields.SafeCharField(unique=True, max_length=100, verbose_name='Domain name')),
                ('validated', models.BooleanField(default=False, help_text='Used to know if the owner actual owns the domain', verbose_name='Validated')),
                ('validation_key', models.CharField(max_length=100, null=True, verbose_name='Domain validation key', blank=True)),
                ('owner', models.ForeignKey(verbose_name='Identified domain owner', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Domain',
                'verbose_name_plural': 'Domains',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DomainTeamMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Membership date')),
                ('domain', models.ForeignKey(verbose_name='Domain', to='domain.Domain')),
                ('member', models.ForeignKey(related_name='domain_teams', verbose_name='Member', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Domain team membership',
                'verbose_name_plural': 'Domain team memberships',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DomainToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, verbose_name='Domain name')),
                ('token', models.CharField(unique=True, max_length=100, verbose_name='Token')),
            ],
            options={
                'verbose_name': 'Domain token',
                'verbose_name_plural': 'Domain tokens',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='domain',
            name='team',
            field=models.ManyToManyField(related_name='team_domains', verbose_name='Team', through='domain.DomainTeamMembership', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
