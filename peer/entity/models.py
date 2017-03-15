# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
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

from datetime import datetime
from lxml import etree
from urlparse import urlparse
import logging

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_fsm import FSMField, transition
from vff.field import VersionedFileField

from peer.customfields import SafeCharField
from peer.domain.models import Domain
from peer.entity.managers import EntityManager
from peer.entity.utils import NAMESPACES, addns, delns, getlang
from peer.entity.utils import expand_settings_permissions
from peer.entity.utils import FetchError, fetch_resource
from peer.entity.utils import write_temp_file
from peer.entity.nagios import send_nagios_notification
from peer.entity.metadata import Metadata, CERTIFICATIONS
from peer.entity.metadata import SP_CATEGORIES, IDP_CATEGORIES
from peer.entity.metadata import MDUI_TR


logger = logging.getLogger(__name__)


CONNECTION_TIMEOUT = 10


class Entity(models.Model):
    app_label = 'peer.entity'

    class STATE:
        NEW = 'new'
        INC = 'incomplete'
        MOD = 'modified'
        PUB = 'published'

    state = FSMField(default=STATE.NEW, protected=True, verbose_name=_(u'Status'))
    metadata = VersionedFileField('metadata', verbose_name=_(u'Entity metadata'),
                                  blank=True, null=True, )
    temp_metadata = models.TextField(default='', verbose_name=_(u'Metadata pending review'), blank=True, null=True)
    diff_metadata = models.TextField(verbose_name=_(u'Diff pending review'), blank=True, null=True)
    owner = models.ForeignKey(User, verbose_name=_('Owner'),
                              blank=True, null=True)
    domain = models.ForeignKey(Domain, verbose_name=_('Domain'))
    delegates = models.ManyToManyField(User, verbose_name=_('Delegates'),
                                       related_name='permission_delegated',
                                       through='PermissionDelegation')
    moderators = models.ManyToManyField(User, verbose_name=_(u'Delegated Moderators'),
                                        related_name='moderation_delegated',
                                        through='ModerationDelegation')
    creation_time = models.DateTimeField(verbose_name=_(u'Creation time'),
                                         auto_now_add=True)
    modification_time = models.DateTimeField(verbose_name=_(u'Modification time'),
                                             auto_now=True)
    subscribers = models.ManyToManyField(User, verbose_name=_('Subscribers'),
                                         related_name='monitor_entities')

    FREQ_CHOICES = (
        ('N', 'Never'),
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )

    metarefresh_frequency = models.CharField(
        verbose_name=_(u'Metadata refreshing frequency'),
        max_length=1,
        choices=FREQ_CHOICES,
        default='N',  # Never
        db_index=True,
    )

    metarefresh_last_run = models.DateTimeField(
        verbose_name=_(u'Last time refreshed'),
        auto_now_add=True,
    )

    objects = EntityManager()

    def __unicode__(self):

        result = unicode(self.id)
        if self.has_metadata():
            if self.display_name:
                result = self.display_name
            elif self.entityid:
                result = self.entityid
            else:
                result += u' (no display name or entityid)'
        else:
            result += u' (no metadata yet)'
        return result

    @models.permalink
    def get_absolute_url(self):
        return ('entities:entity_view', (str(self.id), ))

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')
        ordering = ('-creation_time', )
        permissions = expand_settings_permissions(include_xpath=False)


    def _load_metadata(self):
        if ((not hasattr(self, '_parsed_metadata')) or
                self._parsed_metadata is None):
            if settings.MODERATION_ENABLED:
                if self.temp_metadata != '' and self.state != 'published':
                    data = self.temp_metadata
                else:
                    data = self.metadata.read()
            else:
                data = self.metadata.read()
            if not data:
                raise ValueError('no metadata content')
            if type(data) == unicode:
                data = data.encode('utf-8')
            try:
                metadata_tree = etree.XML(data)
            except etree.XMLSyntaxError:
                raise ValueError('invalid metadata XML')

            md = Metadata(metadata_tree)

            if self.mdui.count():
                for mdui in self.mdui.all():
                    md.add_mdui(mdui)

            if self.contact_people.count():
                for contact in self.contact_people.all():
                    md.add_contact(contact)
            try:
                sp_categories = self.sp_categories
            except SPEntityCategory.DoesNotExist:
                pass
            else:
                md.add_sp_categories(sp_categories)
            try:
                idp_categories = self.idp_categories
            except IdPEntityCategory.DoesNotExist:
                pass
            else:
                md.add_idp_categories(idp_categories)

            self._parsed_metadata = md.etree
            return md

        return Metadata(self._parsed_metadata)

    def has_metadata(self):
        try:
            self._load_metadata()
        except (ValueError, IOError):
            return False
        else:
            return True

    @property
    def entityid(self):
        return self._load_metadata().entityid

    @property
    def display_name(self):
        return self._load_metadata().display_name

    @property
    def valid_until(self):
        return self._load_metadata().valid_until

    @property
    def organization_name(self):
        return self._load_metadata().organization_name

    @property
    def organization(self):
        return self._load_metadata().organization

    @property
    def contacts(self):
        return self._load_metadata().contacts

    @property
    def certificates(self):
        return self._load_metadata().certificates

    @property
    def endpoints(self):
        return self._load_metadata().endpoints

    @property
    def geolocationhint(self):
        return self._load_metadata().geolocationhint

    @property
    def role_descriptor(self):
        return self._load_metadata().role_descriptor

    @property
    def description(self):
        return self._load_metadata().description

    @property
    def attributes(self):
        return self._load_metadata().attributes

    @property
    def logos(self):
        return self._load_metadata().logos

    @property
    def sp_categorization(self):
        return self._load_metadata().sp_categories

    @property
    def idp_categorization(self):
        return self._load_metadata().idp_categories

    @property
    def certifications(self):
        return self._load_metadata().certifications

    @property
    def privacy_statement_url(self):
        return self._load_metadata().privacy_statement_url

    @property
    def security_contact_email(self):
        return self._load_metadata().security_contact_email

    @property
    def metadata_etree(self):
        if self.has_metadata():
            return self._load_metadata().etree
        else:
            return None

    def is_expired(self):
        return (self.has_metadata() and self.valid_until
                and datetime.now() > self.valid_until)

    @property
    def is_metarefreshable(self):
        result = False
        try:
            entityid = self.entityid
        except IOError:
            return result
        if isinstance(entityid, basestring):
            url = urlparse(entityid)
            result = bool(url.scheme.startswith('http'))
            result = result and bool(url.netloc.split('.')[0])
        return result

    def metarefresh(self):

        noid_msg = "Error: Entity %s doesn't have entityid" % (self.id)

        if not hasattr(self, 'entityid'):
            return noid_msg

        url = self.entityid
        if not url:
            return noid_msg

        try:
            text = fetch_resource(url)
            if text is None:
                text = fetch_resource('http://' + url)

                if text is None:
                    return 'Unknown error while fetching the url'
        except FetchError as e:
            return str(e)

        if not text:
            return 'Empty metadata not allowed'

        content = write_temp_file(text)
        name = self.metadata.name
        commit_msg = 'Updated automatically from %s' % (url)
        self.metadata.save(name, content, self.owner.username, commit_msg)

        self.metarefresh_last_run = datetime.now()
        self.save()

        return 'Success: Data was updated successfully'

    def _store_certifications_database(self, metadata, cats):
        if metadata.has_assurance_certification_el():
            certifications = self.certifications
            cats.sirtfi_id_assurance = CERTIFICATIONS['SIRTFI'] in certifications
            if cats.sirtfi_id_assurance:
                sce = self.security_contact_email
                if sce is None:
                    raise ValueError(_('To certify an entity with '
                        'SIRTFI identity assurance, you must provide a '
                        'security contact email'))
                cats.security_contact_email = sce

    def store_spcategory_database(self, metadata=None):
        if metadata is None:
            metadata = self._load_metadata()
        if (metadata.has_categories_el() or
                metadata.has_assurance_certification_el()):
            sp_cats, created = SPEntityCategory.objects.get_or_create(entity=self)
        else:
            return
        if metadata.has_categories_el():
            categories = metadata.sp_categories
            sp_cats.research_and_scholarship = SP_CATEGORIES['R&S'] in categories
            sp_cats.code_of_conduct = SP_CATEGORIES['CoCo'] in categories
            sp_cats.research_and_education = SP_CATEGORIES['R&E'] in categories
            sp_cats.rae_hei_service = SP_CATEGORIES['HEI'] in categories
            sp_cats.rae_nren_service = SP_CATEGORIES['NREN'] in categories
            sp_cats.rae_eu_protection = SP_CATEGORIES['EU'] in categories
            sp_cats.swamid_sfs = SP_CATEGORIES['SFS'] in categories
            if (not sp_cats.research_and_education) and (sp_cats.rae_hei_service or
                    sp_cats.rae_hei_service or sp_cats.rae_eu_protection):
                raise ValueError(_('To categorize the entity with the '
                    'HEI service, NREN service, or EU protection categories, '
                    'you also need to categorize it for Research & Education'))
            if sp_cats.code_of_conduct:
                lang, psu = self.privacy_statement_url
                if psu is None:
                    raise ValueError(_('To categorize an entity with the '
                        'GEANT Code of Conduct category, you must provide a '
                        'privacy statement URL'))
                sp_cats.coc_priv_statement_url = psu
                sp_cats.lang_priv_statement_url = getlang(psu)
        self._store_certifications_database(metadata, sp_cats)
        sp_cats.save()

    def store_idpcategory_database(self, metadata=None):
        if metadata is None:
            metadata = self._load_metadata()
        if (metadata.has_categories_support_el() or
                metadata.has_assurance_certification_el()):
            idp_cats, created = IdPEntityCategory.objects.get_or_create(entity=self)
        else:
            return
        if metadata.has_categories_support_el():
            categories = metadata.idp_categories
            idp_cats.research_and_scholarship = IDP_CATEGORIES['R&S'] in categories
            idp_cats.code_of_conduct = IDP_CATEGORIES['CoCo'] in categories
            if idp_cats.code_of_conduct:
                lang, psu = self.privacy_statement_url
                if psu is None:
                    raise ValueError(_('To categorize an entity with support '
                        'for the GEANT Code of Conduct category, you must provide a '
                        'privacy statement URL'))
                idp_cats.coc_priv_statement_url = psu
                idp_cats.lang_priv_statement_url = lang
        self._store_certifications_database(metadata, idp_cats)
        idp_cats.save()

    def store_mdui_database(self, metadata=None):
        if metadata is None:
            metadata = self._load_metadata()
        if not metadata.has_uiinfo_el():
            return
        for language in settings.MDUI_LANGS:
            lang = language[0]
            mdui, created = MDUIdata.objects.get_or_create(entity=self, lang=lang)
            for attr,tag in MDUI_TR.items():
                data_el = metadata.get_mdui_info_piece(tag, lang)
                data = data_el.text if data_el is not None else None
                setattr(mdui, attr, data)
                if data_el is not None and attr == 'logo':
                    mdui.logo_height = data_el.attrib['height']
                    mdui.logo_width = data_el.attrib['width']
            mdui.save()

    def store_contacts_database(self, metadata=None):
        if metadata is None:
            metadata = self._load_metadata()
        for t in ContactPerson.CONTACT_TYPES:
            type = t[0]
            contact, created = ContactPerson.objects.get_or_create(entity=self, type=type)
            email = metadata.get_contact_data('EmailAddress', type)
            if not email:
                raise ValueError(_('You must provide an email for every contact'))
            elif email.startswith('mailto'):
                email = email[7:]
            contact.email = email
            contact.name = metadata.get_contact_data('SurName', type)
            contact.phone = metadata.get_contact_data('TelephoneNumber', type)
            contact.save()

    def revert_category_changes(self):
        md_str = self.metadata.read()
        metadata = Metadata(etree.XML(md_str))
        try:
            self.store_idpcategory_database(metadata)
            self.store_spcategory_database(metadata)
            self.store_mdui_database(metadata)
            self.store_contacts_database(metadata)
        except ValueError:
            # XXX set entity as incomplete, send message to user
            pass

    def check_complete(self):
        missing = []
        md = self._load_metadata()
        for language in settings.MDUI_LANGS:
            lang = language[0]
            for tag in []:
                pass
            

    @transition(field=state, source='*', target=STATE.MOD)
    def modify(self, temp_metadata):
        self.temp_metadata = temp_metadata

    @transition(field=state, source='*', target=STATE.PUB)
    def approve(self, name, content, username, commit_msg):
        self.temp_metadata = ''
        self.metadata.save(name, content, username, commit_msg)

    @transition(field=state, source=STATE.MOD, target=STATE.PUB)
    def reject(self):
        self.revert_category_changes()
        self.temp_metadata = ''


def handler_entity_pre_save(sender, instance, **kwargs):
    if not instance.is_metarefreshable:
        instance.metarefresh_frequency = 'N'  # Never


models.signals.pre_save.connect(handler_entity_pre_save, sender=Entity)


def handler_entity_post_save(sender, instance, created, **kwargs):
    action = created and 'Entity created' or 'Entity updated'
    send_nagios_notification(instance.domain, action)


def handler_entity_post_delete(sender, instance, **kwargs):
    send_nagios_notification(instance.domain, 'Entity deleted')


if hasattr(settings, 'NSCA_COMMAND') and settings.NSCA_COMMAND:
    models.signals.post_save.connect(handler_entity_post_save, sender=Entity)
    models.signals.post_delete.connect(handler_entity_post_delete, sender=Entity)


class SPEntityCategory(models.Model):
    entity = models.OneToOneField(Entity,
                                  verbose_name=_(u'Entity'),
                                  related_name='sp_categories',
                                  primary_key=True)
    research_and_scholarship = models.BooleanField(_('REFEDS Research and Scholarship'),
                                                                default=False)
    code_of_conduct = models.BooleanField(_('GEANT Code of Conduct'), default=False)
    coc_priv_statement_url = models.URLField(_('Privacy Statement URL'), null=True, blank=True)
    lang_priv_statement_url = models.CharField(max_length=2,
                                            verbose_name=_('Privacy statement language'),
                                            choices=settings.MDUI_LANGS)
    research_and_education = models.BooleanField(_('SWAMID Research and Education'),
                                                                default=False)
    swamid_sfs = models.BooleanField(_('SWAMID SFS'), default=False)
    rae_hei_service =  models.BooleanField(_('SWAMID HEI Service'), default=False)
    rae_nren_service =  models.BooleanField(_('SWAMID NREN Service'), default=False)
    rae_eu_protection =  models.BooleanField(_('SWAMID EU Adequate Protection'), default=False)
    sirtfi_id_assurance =  models.BooleanField(_('REFEDS SIRTFI Identity Assurance Certification'),
                                                                 default=False)
    security_contact_email = models.EmailField(_('Security Contact Email'), null=True, blank=True)


def handler_cat_post_save(sender, instance, **kwargs):
    if instance.coc_priv_statement_url and instance.lang_priv_statement_url:
        mdui, created = MDUIdata.objects.get_or_create(entity=instance.entity,
                                                lang=instance.lang_priv_statement_url)
        if mdui.priv_statement_url != instance.coc_priv_statement_url:
            mdui.priv_statement_url = instance.coc_priv_statement_url
            mdui.save()

models.signals.post_save.connect(handler_cat_post_save, sender=SPEntityCategory)


class IdPEntityCategory(models.Model):
    entity = models.OneToOneField(Entity,
                                  verbose_name=_(u'Entity'),
                                  related_name='idp_categories',
                                  primary_key=True)
    research_and_scholarship = models.BooleanField(_('REFEDS Research and Scholarship'),
                                                                default=False)
    code_of_conduct = models.BooleanField(_('GEANT Code of Conduct'), default=False)
    coc_priv_statement_url = models.URLField(_('Privacy Statement URL'), null=True, blank=True)
    lang_priv_statement_url = models.CharField(max_length=2,
                                            verbose_name=_('Privacy statement language'),
                                            choices=settings.MDUI_LANGS)
    sirtfi_id_assurance =  models.BooleanField(_('REFEDS SIRTFI Identity Assurance Certification'),
                                                                 default=False)
    security_contact_email = models.EmailField(_('Security Contact Email'), null=True, blank=True)

models.signals.post_save.connect(handler_cat_post_save, sender=IdPEntityCategory)


class MDUIdata(models.Model):
    entity = models.ForeignKey(Entity,
                               verbose_name=_(u'Entity'),
                               related_name='mdui')
    lang = models.CharField(max_length=2,
                            verbose_name=_('Language'),
                            choices=settings.MDUI_LANGS)
    display_name = models.CharField(max_length=255, verbose_name=_('Display Name'),
                                    blank=True, null=True)
    description = models.TextField(verbose_name=_(u'Description'),
                                   blank=True, null=True)
    priv_statement_url = models.URLField(verbose_name=_('Privacy Statement URL'),
                                         blank=True, null=True)
    information_url = models.URLField(verbose_name=_('Information URL'),
                                         blank=True, null=True)
    logo = models.URLField(verbose_name=_('Logo'), blank=True, null=True)
    logo_height = models.PositiveSmallIntegerField(verbose_name=_('Height of the logo'),
                                          blank=True, null=True)
    logo_width = models.PositiveSmallIntegerField(verbose_name=_('Width of the logo'),
                                          blank=True, null=True)


def handler_mdui_post_save(sender, instance, **kwargs):
    if instance.priv_statement_url:
        if instance.entity.role_descriptor == 'SP':
            cats, created = SPEntityCategory.objects.get_or_create(entity=instance.entity)
        else:
            cats, created = IdPEntityCategory.objects.get_or_create(entity=instance.entity)
        if cats.coc_priv_statement_url != instance.priv_statement_url:
            cats.coc_priv_statement_url = instance.priv_statement_url
            cats.lang_priv_statement_url = instance.lang
            cats.save()

models.signals.post_save.connect(handler_mdui_post_save, sender=MDUIdata)


class EntityGroup(models.Model):
    app_label = 'peer.entity'
    name = SafeCharField(_(u'Name of the group'), max_length=200)
    query = SafeCharField(_(u'Query that defines the group'), max_length=100)
    owner = models.ForeignKey(User, verbose_name=_('Owner'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Entity group')
        verbose_name_plural = _('Entity groups')


class PermissionDelegation(models.Model):
    app_label = 'peer.entity'
    entity = models.ForeignKey(Entity, verbose_name=_(u'Entity'))
    delegate = models.ForeignKey(User, verbose_name=_('Delegate'),
                                 related_name='permission_delegate')
    date = models.DateTimeField(_(u'Delegation date'),
                                default=datetime.now)

    def __unicode__(self):
        return ugettext(
            u'%(user)s delegates permissions for %(entity)s entity') % {
            'user': self.entity.owner.username, 'entity': unicode(self.entity)}

    class Meta:
        verbose_name = _(u'Permission delegation')
        verbose_name_plural = _(u'Permission delegations')


class ModerationDelegation(models.Model):
    app_label = 'peer.entity'
    entity = models.ForeignKey(Entity, verbose_name=_(u'Entity'))
    moderator = models.ForeignKey(User, verbose_name=_(u'Moderator'), related_name='delegated_moderator')

    def __unicode__(self):
        return ugettext(
            u'Moderation for %(entity)s delegated to %(user)s') % {'entity': unicode(self.entity), 'user': unicode(self.moderator.username)}

    class Meta:
        verbose_name = _(u'Moderation delegation')
        verbose_name_plural = _(u'Moderation delegations')

ROLE_CHOICES = (('SP', 'Service Provider'),
                ('IDP', 'Identity Provider'),
                ('both', 'Both'))


class EntityMD(models.Model):
    entity = models.OneToOneField(Entity, verbose_name=_(u'Entity'), primary_key=True)
    entityid = models.CharField(null=True, max_length=250)
    domain = models.ForeignKey(Domain, verbose_name=_('Domain'))
    superdomain = models.ForeignKey(Domain, verbose_name=_('Superdomain'),
                                    null=True, related_name='entities_md')
    description = models.TextField(null=True)
    display_name = models.CharField(null=True, max_length=250)
    organization = models.CharField(null=True, max_length=250)
    role_descriptor = models.CharField(null=True,
                                       max_length=4,
                                       choices=ROLE_CHOICES)


class AttributesMD(models.Model):
    entity_md = models.ForeignKey(EntityMD, verbose_name=_(u'Entity metadata'))
    friendly_name = models.CharField(null=True, max_length=250)
    name = models.CharField(null=True, max_length=250)
    name_format = models.CharField(null=True, max_length=250)
    value = models.CharField(null=True, max_length=250)


class ContactPerson(models.Model):

    CONTACT_TYPES = (
        ('S', 'support'),
        ('A', 'administrative'),
        ('T', 'technical'),
    )

    entity = models.ForeignKey(Entity,
            verbose_name=_(u'Entity'),
            related_name='contact_people')
    type = models.CharField(_(u'Contact type'),
            max_length=2, choices=CONTACT_TYPES,
            blank=True, null=True)
    email = models.EmailField(_('Email address'),
            null=True, blank=True)
    name = models.TextField(_(u'Name'),
            blank=True, null=True)
    phone = models.CharField(_(u'Phone number'),
            max_length=255, blank=True, null=True)
