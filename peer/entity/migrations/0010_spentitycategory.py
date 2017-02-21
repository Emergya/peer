# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0009_entitymd_superdomain'),
    ]

    operations = [
        migrations.CreateModel(
            name='SPEntityCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('research_and_scholarship', models.BooleanField(default=False, verbose_name='REFEDS Research and Scholarship')),
                ('code_of_conduct', models.BooleanField(default=False, verbose_name='GEANT Code of Conduct')),
                ('coc_priv_statement_url', models.URLField(null=True, verbose_name='Privacy Statement URL', blank=True)),
                ('research_and_education', models.BooleanField(default=False, verbose_name='SWAMID Research and Education')),
                ('swamid_sfs', models.BooleanField(default=False, verbose_name='SWAMID SFS')),
                ('rae_hei_service', models.BooleanField(default=False, verbose_name='SWAMID HEI Service')),
                ('rae_nren_service', models.BooleanField(default=False, verbose_name='SWAMID NREN Service')),
                ('rae_eu_protection', models.BooleanField(default=False, verbose_name='SWAMID EU Adequate Protection')),
                ('sirtfi_id_assurance', models.BooleanField(default=False, verbose_name='REFEDS SIRTFI Identity Assurance Certification')),
                ('security_contact_email', models.EmailField(max_length=254, null=True, verbose_name='Security Contact Email', blank=True)),
                ('entity', models.ForeignKey(verbose_name='Entity', to='entity.Entity')),
            ],
        ),
    ]
