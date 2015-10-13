# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0005_auto_20150715_0754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='state',
            field=django_fsm.FSMField(default=b'new', protected=True, max_length=50, verbose_name='Status'),
        ),
    ]
