# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0007_auto_20151007_0741'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitymd',
            name='entityid',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
