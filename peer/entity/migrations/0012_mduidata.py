# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0011_auto_20170308_1010'),
    ]

    operations = [
        migrations.CreateModel(
            name='MDUIdata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=2, verbose_name='Language', choices=[(b'en', b'English'), (b'sv', b'Svenska')])),
                ('display_name', models.CharField(max_length=255, verbose_name='Display Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('priv_statement_url', models.URLField(null=True, verbose_name='Privacy Statement URL', blank=True)),
                ('information_url', models.URLField(null=True, verbose_name='Information URL', blank=True)),
                ('entity', models.ForeignKey(related_name='mdui', verbose_name='Entity', to='entity.Entity')),
            ],
        ),
    ]
