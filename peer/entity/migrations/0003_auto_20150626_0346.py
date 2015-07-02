# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20150624_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderationdelegation',
            name='moderator',
            field=models.ForeignKey(related_name='delegated_moderator', verbose_name='Moderator', to=settings.AUTH_USER_MODEL),
        ),
    ]
