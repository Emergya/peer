# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0002_auto_20150624_0859'),
        ('entity', '0003_auto_20150626_0346'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributesMD',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('friendly_name', models.CharField(max_length=200, null=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('name_format', models.CharField(max_length=200, null=True)),
                ('value', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EntityMD',
            fields=[
                ('entity', models.OneToOneField(primary_key=True, serialize=False, to='entity.Entity', verbose_name='Entity')),
                ('description', models.CharField(max_length=200, null=True)),
                ('display_name', models.CharField(max_length=200, null=True)),
                ('organization', models.CharField(max_length=200, null=True)),
                ('role_descriptor', models.CharField(max_length=4, null=True, choices=[(b'SP', b'Service Provider'), (b'IDP', b'Identity Provider'), (b'both', b'Both')])),
                ('domain', models.ForeignKey(verbose_name='Domain', to='domain.Domain')),
            ],
        ),
        migrations.AddField(
            model_name='attributesmd',
            name='entity_md',
            field=models.ForeignKey(verbose_name='Entity metadata', to='entity.EntityMD'),
        ),
        migrations.AlterUniqueTogether(
            name='attributesmd',
            unique_together=set([('entity_md', 'friendly_name', 'name', 'name_format', 'value')]),
        ),
    ]
