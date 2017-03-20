# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0016_auto_20170315_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactperson',
            name='given_name',
            field=models.TextField(null=True, verbose_name='Given Name', blank=True),
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='name',
            field=models.TextField(null=True, verbose_name='Surname', blank=True),
        ),
    ]
