# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0015_contactperson'),
    ]

    operations = [
        migrations.AddField(
            model_name='mduidata',
            name='logo',
            field=models.URLField(null=True, verbose_name='Logo', blank=True),
        ),
        migrations.AddField(
            model_name='mduidata',
            name='logo_height',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Height of the logo', blank=True),
        ),
        migrations.AddField(
            model_name='mduidata',
            name='logo_width',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Width of the logo', blank=True),
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='entity',
            field=models.ForeignKey(related_name='contact_people', verbose_name='Entity', to='entity.Entity'),
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='type',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Contact type', choices=[(b'S', b'support'), (b'A', b'administrative'), (b'T', b'technical')]),
        ),
    ]
