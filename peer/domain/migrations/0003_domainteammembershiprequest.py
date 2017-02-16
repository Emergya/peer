# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domain', '0002_auto_20150624_0859'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainTeamMembershipRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Request date')),
                ('domain', models.ForeignKey(related_name='membership_requests', verbose_name='Domain', to='domain.Domain')),
                ('requester', models.ForeignKey(related_name='domain_membership_requests', verbose_name='Requester', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Domain team membership request',
                'verbose_name_plural': 'Domain team membership requests',
            },
        ),
    ]
