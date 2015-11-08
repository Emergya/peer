# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0002_auto_20150624_0859'),
        ('entity', '0008_entitymd_entityid'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitymd',
            name='superdomain',
            field=models.ForeignKey(related_name='entities_md', verbose_name='Superdomain', to='domain.Domain', null=True),
        ),
    ]
