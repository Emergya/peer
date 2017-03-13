# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0013_auto_20170310_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='idpentitycategory',
            name='lang_priv_statement_url',
            field=models.CharField(default='en', max_length=2, verbose_name='Privacy statement language', choices=[(b'en', b'English'), (b'sv', b'Svenska')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spentitycategory',
            name='lang_priv_statement_url',
            field=models.CharField(default='en', max_length=2, verbose_name='Privacy statement language', choices=[(b'en', b'English'), (b'sv', b'Svenska')]),
            preserve_default=False,
        ),
    ]
