# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0014_auto_20170313_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactPerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(blank=True, max_length=2, null=True, verbose_name='Phone number', choices=[(b'S', b'Support'), (b'A', b'Administrative'), (b'T', b'Technical')])),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='Email address', blank=True)),
                ('name', models.TextField(null=True, verbose_name='Name', blank=True)),
                ('phone', models.CharField(max_length=255, null=True, verbose_name='Phone number', blank=True)),
                ('entity', models.ForeignKey(related_name='contacts', verbose_name='Entity', to='entity.Entity')),
            ],
        ),
    ]
