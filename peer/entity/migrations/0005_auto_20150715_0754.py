# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_auto_20150715_0535'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attributesmd',
            unique_together=set([]),
        ),
    ]
