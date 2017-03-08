# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0010_spentitycategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdPEntityCategory',
            fields=[
                ('entity', models.OneToOneField(related_name='idp_categories', primary_key=True, serialize=False, to='entity.Entity', verbose_name='Entity')),
                ('research_and_scholarship', models.BooleanField(default=False, verbose_name='REFEDS Research and Scholarship')),
                ('code_of_conduct', models.BooleanField(default=False, verbose_name='GEANT Code of Conduct')),
                ('coc_priv_statement_url', models.URLField(null=True, verbose_name='Privacy Statement URL', blank=True)),
                ('sirtfi_id_assurance', models.BooleanField(default=False, verbose_name='REFEDS SIRTFI Identity Assurance Certification')),
                ('security_contact_email', models.EmailField(max_length=254, null=True, verbose_name='Security Contact Email', blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='spentitycategory',
            name='id',
        ),
        migrations.AlterField(
            model_name='spentitycategory',
            name='entity',
            field=models.OneToOneField(related_name='sp_categories', primary_key=True, serialize=False, to='entity.Entity', verbose_name='Entity'),
        ),
    ]
