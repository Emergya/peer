# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Terena.

import difflib
from lxml import etree

from django import forms
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as U
from django.conf import settings

from peer.account.templatetags.account import authorname
from peer.customfields import TermsOfUseField, readtou
from peer.entity.models import Entity, EntityGroup, EntityMD, AttributesMD
from peer.entity.models import SPEntityCategory
from peer.entity.validation import validate
from peer.domain.validation import get_superdomain_verified
from peer.entity.widgets import MetadataWidget
from peer.entity.utils import FetchError, fetch_resource
from peer.entity.utils import write_temp_file, strip_entities_descriptor
from peer.entity.models import SP_CATEGORIES


class EntityForm(forms.ModelForm):

    class Meta:
        model = Entity
        fields = ('domain', )

    def __init__(self, user, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['domain'].queryset = self.fields['domain'].queryset.filter(
            Q(owner=self.user, validated=True) |
            Q(team=self.user, validated=True)).distinct()
        self.fields['domain'].label = U(u'Select Domain')
        self.fields['domain'].help_text = U(
            u'You need to associate the entity with a domain.')

    def clean_domain(self):
        domain = self.cleaned_data.get('domain')
        if domain and domain.owner != self.user and \
                self.user not in domain.team.all():
            raise forms.ValidationError(U('You cannot use this domain'))

        return domain

    def clean(self):
        name = self.cleaned_data.get('name')
        domain = self.cleaned_data.get('domain')

        if name and domain:
            for ch in r'!:&\|':
                if ch in name:
                    raise forms.ValidationError(U('Illegal characters in the name: '
                                                  'You cannot use &, |, !, : or \\'))
            try:
                Entity.objects.get(name=name, domain=domain)
                raise forms.ValidationError(U('There is already an entity with that name for that domain'))
            except Entity.DoesNotExist:
                pass

        return self.cleaned_data


class EntityGroupForm(forms.ModelForm):

    class Meta:
        model = EntityGroup
        fields = ('name', 'query')
        widgets = {
            'query': forms.TextInput(attrs={'class': 'longInput'}),
        }


def commitMessageWidgetFactory():
    return forms.CharField(
        required=True,
        label=_('Commit message'),
        help_text=_('Short description of the commited changes'),
        widget=forms.TextInput(attrs={'class': 'commitMessage'}),
    )


def check_metadata_is_new(entity, new_metadata):
    old_metadata = entity.metadata.get_revision()
    if old_metadata == new_metadata:
        raise forms.ValidationError('There are no changes in the metadata')


def check_metadata_is_valid(form, entity, user, new_metadata, field):
    if type(new_metadata) != unicode:
        new_metadata = new_metadata.decode('utf-8', 'ignore')
    errors = validate(entity, new_metadata, user)
    if errors:
        # We don't raise ValidationError since we can have multiple errors
        form._errors[field] = form.error_class(errors)
        del form.cleaned_data[field]


class BaseMetadataEditForm(forms.Form):

    type = ''

    def __init__(self, entity, user, *args, **kwargs):
        self.entity = entity
        self.user = user
        self.metadata = None
        super(BaseMetadataEditForm, self).__init__(*args, **kwargs)

    def _clean_metadata_field(self, fieldname):
        data = self.cleaned_data[fieldname]
        if hasattr(data, 'strip'):
            data = data.strip()

        if not data:
            raise forms.ValidationError('Empty metadata is not allowed')

        metadata = self._field_value_to_metadata(data)
        if type(metadata) == unicode:
            metadata = metadata.encode('utf8')
        if not metadata:
            raise forms.ValidationError('Empty metadata is not allowed')

        check_metadata_is_new(self.entity, metadata)
        check_metadata_is_valid(
            self, self.entity, self.user, metadata, fieldname)

        try:
            metadata = strip_entities_descriptor(metadata)
        except ValueError as e:
            raise forms.ValidationError(unicode(e))

        self.metadata = metadata

        return data

    def _field_value_to_metadata(self, field_value):
        return field_value

    def get_metadata(self):
        return self.metadata

    def get_diff(self):
        text1 = self.entity.metadata.get_revision()
        if type(text1) != unicode:
            text1 = text1.decode('utf-8', 'ignore')
        text2 = self.metadata
        if type(text2) != unicode:
            text2 = text2.decode('utf-8', 'ignore')
        return u'\n'.join(difflib.unified_diff(text1.split('\n'), text2.split('\n')))

    def save(self, action):
        content = write_temp_file(self.metadata)
        name = self.entity.metadata.name
        username = authorname(self.user)
        commit_msg = self.cleaned_data['commit_msg_' + self.type].encode('utf8')
        if settings.MODERATION_ENABLED:
            if action == 'submit_changes':
                self.entity.modify(self.metadata)
            elif action == 'approve_changes':
                self.entity.approve(name, content, username, commit_msg)
            elif action == 'discard_changes':
                self.entity.reject()
        else:
            self.entity.metadata.save(name, content, username, commit_msg)
        self.entity.save()
        self.store_entitymd_database(self.entity.id)
        self.store_spcategory_database(self.entity.id)
        mail_owner = True if self.entity.owner != self.user else False
        if mail_owner:
            if not settings.MODERATION_ENABLED:
                action = 'modified'
            else:
                if action == 'submit_changes':
                    action = 'submitted changes for'
                if action == 'approve_changes':
                    action = 'approved changes for'
                if action == 'discard_changes':
                    action = 'discarded changes for'
            msg = ('Dear {owner},\n{moderator} has {action} the entity '
                    'with EntityID {entityid}.'.format(
                        owner=unicode(self.entity.owner),
                        moderator=unicode(self.user),
                        action=action.replace('_', ' '),
                        entityid=self.entity.entityid))
            send_mail('Entity modified', msg, settings.DEFAULT_FROM_EMAIL,
                    [self.entity.owner.email])

    def store_entitymd_database(self, id_ent):
        entity = Entity.objects.get(id=id_ent)
        ent_md, created = EntityMD.objects.get_or_create(entity=entity, domain=entity.domain)
        ent_md.entityid = entity.entityid
        ent_md.description = entity.description
        ent_md.display_name = entity.display_name
        ent_md.organization = entity.organization_name
        ent_md.role_descriptor = entity.role_descriptor
        superdomain = get_superdomain_verified(entity.domain.name)
        if superdomain:
            ent_md.superdomain = superdomain
        ent_md.save()
        AttributesMD.objects.filter(entity_md=ent_md).delete()
        for attr in entity.attributes:
            AttributesMD.objects.create(entity_md=ent_md,
                                        name=attr.get('Name'),
                                        name_format=attr.get('NameFormat'),
                                        value=attr.get('Value'),
                                        friendly_name=attr.get('FriendlyName'))

    def store_spcategory_database(self, id_ent):
        entity = Entity.objects.get(id=id_ent)
        if (entity._load_metadata().has_categories_el() or
                entity._load_metadata().has_assurance_certification_el()):
            sp_cats, created = SPEntityCategory.objects.get_or_create(entity=entity)
        if entity._load_metadata().has_categories_el():
            categories = entity.sp_categorization
            sp_cats.research_and_scholarship = SP_CATEGORIES['R&S'] in categories
            sp_cats.code_of_conduct = SP_CATEGORIES['CoCo'] in categories
            sp_cats.research_and_education = SP_CATEGORIES['R&E'] in categories
            sp_cats.rae_hei_service = SP_CATEGORIES['HEI'] in categories
            sp_cats.rae_nren_service = SP_CATEGORIES['NREN'] in categories
            sp_cats.rae_eu_protection = SP_CATEGORIES['EU'] in categories
            sp_cats.swamid_sfs = SP_CATEGORIES['SFS'] in categories
            if (not sp_cats.research_and_education) and (sp_cats.rae_hei_service or
                    sp_cats.rae_hei_service or sp_cats.rae_eu_protection):
                raise forms.ValidationError(_('To categorize the entity with the '
                    'HEI service, NREN service, or EU protection categories, '
                    'you also need to categorize it for Research & Education'))
            if sp_cats.code_of_conduct:
                psu = entity.privacy_statement_url
                if psu is None:
                    raise forms.ValidationError(_('To categorize an entity with the '
                        'GEANT Code of Conduct category, you must provide a '
                        'privacy statement URL'))
                sp_cats.coc_priv_statement_url = psu
        if entity._load_metadata().has_assurance_certification_el():
            certifications = entity.certifications
            sp_cats.sirtfi_id_assurance = SP_CATEGORIES['SIRTFI'] in certifications
            if sp_cats.sirtfi_id_assurance:
                sce = entity.security_contact_email
                if sce is None:
                    raise forms.ValidationError(_('To categorize an entity with the '
                        'SIRTFI identity assurance category, you must provide a '
                        'security contact email'))
                sp_cats.security_contact_email = sce
            sp_cats.save()


class MetadataTextEditForm(BaseMetadataEditForm):

    type = 'text'

    metadata_text = forms.CharField(
        label=_('Metadata'),
        help_text=_('Edit the metadata for this entity'),
        widget=MetadataWidget
    )
    commit_msg_text = commitMessageWidgetFactory()

    def clean_metadata_text(self):
        return self._clean_metadata_field('metadata_text')


class MetadataFileEditForm(BaseMetadataEditForm):

    type = 'file'

    metadata_file = forms.FileField(
        label=_('Metadata'),
        help_text=_('Upload a file with the metadata for this entity'),
    )
    commit_msg_file = commitMessageWidgetFactory()
    tou = TermsOfUseField(readtou('METADATA_IMPORT_TERMS_OF_USE'))

    def clean_metadata_file(self):
        return self._clean_metadata_field('metadata_file')

    def _field_value_to_metadata(self, fileobj):
        data = fileobj.read()
        fileobj.seek(0)
        return data


class MetadataRemoteEditForm(BaseMetadataEditForm):

    type = 'remote'

    metadata_url = forms.URLField(
        required=True,
        label=_('Metadata'),
        help_text=_('Enter the URL of an XML document'
                    ' with the metadata for this entity'),
    )
    commit_msg_remote = commitMessageWidgetFactory()
    tou = TermsOfUseField(readtou('METADATA_IMPORT_TERMS_OF_USE'))

    def clean_metadata_url(self):
        return self._clean_metadata_field('metadata_url')

    def _field_value_to_metadata(self, remote_url):
        try:
            data = fetch_resource(remote_url)
            if data is None:
                data = fetch_resource('http://' + remote_url)

                if data is None:
                    raise forms.ValidationError('Unknown error while fetching the url')
        except FetchError as e:
            raise forms.ValidationError(str(e))

        return data


class EditMetarefreshForm(forms.ModelForm):

    class Meta:
        model = Entity
        fields = ('metarefresh_frequency', )

    def __init__(self, *args, **kwargs):
        super(EditMetarefreshForm, self).__init__(*args, **kwargs)
        field = self.fields['metarefresh_frequency']
        field.widget = forms.RadioSelect()
        field.choices = Entity.FREQ_CHOICES


class EditMonitoringPreferencesForm(forms.Form):

    want_alerts = forms.BooleanField(
        label=_('Receive email alerts when any endpoint of this entity is down'),
        required=False,  # to allow falsy values
    )


class SPEntityCategoryForm(forms.ModelForm):
    class Meta:
        model = SPEntityCategory
        fields = (
            'entity', 'research_and_scholarship',
            'code_of_conduct', 'coc_priv_statement_url',
            'research_and_education', 'rae_eu_protection',
            'rae_hei_service', 'rae_nren_service',
            'swamid_sfs', 'sirtfi_id_assurance',
            'security_contact_email',
            )
        widgets = {
                'entity': forms.HiddenInput()
                }

    def clean(self):
        super(SPEntityCategoryForm, self).clean()
        if (self.cleaned_data['code_of_conduct'] and
                not self.cleaned_data['coc_priv_statement_url']):
            raise forms.ValidationError(U('Checking GEANT Code of Conduct '
                'requires that you provide a privacy statement URL'))
        if not self.cleaned_data['research_and_education']:
            if (self.cleaned_data['rae_hei_service'] or
                    self.cleaned_data['rae_nren_service'] or
                    self.cleaned_data['rae_eu_protection']):
                raise forms.ValidationError(U('You must check SWAMID research and '
                    'education if you want to also check EU adecuate '
                    'protection, or the NREN or HEI services'))
        if (self.cleaned_data['sirtfi_id_assurance'] and
                not self.cleaned_data['security_contact_email']):
            raise forms.ValidationError(U('If you check the SIRTFI Identity '
                'assurance certification, you must provide a '
                'security contact'))

    def save(self, *args, **kwargs):
        super(SPEntityCategoryForm, self).save(*args, **kwargs)
        entity = self.instance.entity
        entity.modify(etree.tostring(entity._load_metadata().etree))
        entity.save()
