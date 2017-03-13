# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0012_mduidata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mduidata',
            name='description',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='mduidata',
            name='display_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Display Name', blank=True),
        ),
    ]
