# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0006_auto_20150930_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributesmd',
            name='friendly_name',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='attributesmd',
            name='name',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='attributesmd',
            name='name_format',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='attributesmd',
            name='value',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='entitymd',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='entitymd',
            name='display_name',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='entitymd',
            name='organization',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
