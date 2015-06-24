# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainModeratorsTeamMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Membership date')),
                ('domain', models.ForeignKey(verbose_name='Domain', to='domain.Domain')),
                ('member', models.ForeignKey(related_name='domain_moderator_teams', verbose_name='Member', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Domain moderator team membership',
                'verbose_name_plural': 'Domain moderator team memberships',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='domain',
            name='moderators',
            field=models.ManyToManyField(related_name='moderator_team_domains', verbose_name='Reviewers', through='domain.DomainModeratorsTeamMembership', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
