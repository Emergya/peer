# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0003_domainteammembershiprequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='owner',
            field=models.ForeignKey(related_name='domains', verbose_name='Identified domain owner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='domainteammembership',
            name='domain',
            field=models.ForeignKey(related_name='team_memberships', verbose_name='Domain', to='domain.Domain'),
        ),
    ]
