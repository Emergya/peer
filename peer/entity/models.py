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

XML_NAMESPACE = NAMESPACES['xml']
XMLDSIG_NAMESPACE = NAMESPACES['ds']
MDUI_NAMESPACE = NAMESPACES['mdui']
MDATTR_NAMESPACE = NAMESPACES['mdattr']
SAML_NAMESPACE = NAMESPACES['saml']

CONNECTION_TIMEOUT = 10


class Metadata(object):
    def __init__(self, etree):
        self.etree = etree

    @property
    def entityid(self):
        if 'entityID' in self.etree.attrib:
            return self.etree.attrib['entityID']

    @property
    def valid_until(self):
        if 'validUntil' in self.etree.attrib:
            value = self.etree.attrib['validUntil']
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:  # Bad datetime format
                pass

    @property
    def organization(self):
        languages = {}
        for org_node in self.etree.findall(addns('Organization')):
            for attr in (('name', 'Name'),
                         ('displayName', 'DisplayName'),
                         ('URL', 'URL')):
                node_name = 'Organization' + attr[1]
                for node in org_node.findall(addns(node_name)):
                    lang = getlang(node)
                    if lang is None:
                        continue  # the lang attribute is required

                    lang_dict = languages.setdefault(lang, {})
                    lang_dict[attr[0]] = node.text

        result = []
        for lang, data in languages.items():
            data['lang'] = lang
            result.append(data)
        return result

    @property
    def organization_name(self):
        org_name = ''
        organizations = self.organization
        for org in organizations:
            if org.get('lang') == 'en':
                org_name = org.get('name')
        if org_name == '' and len(organizations) > 0:
            org_name = organizations[0].get('lang')
        return org_name

    @property
    def contacts(self):
        result = []
        for contact_node in self.etree.findall(addns('ContactPerson')):
            contact = {}

            if 'contactType' in contact_node.attrib:
                contact['type'] = contact_node.attrib['contactType']

            for child in contact_node:
                contact[delns(child.tag)] = child.text

            result.append(contact)
        return result

    @property
    def certificates(self):
        result = []

        def collect_certificates_for_role(role):
            key_descr_path = [addns(role), addns('KeyDescriptor')]

            for key_descriptor in self.etree.findall('/'.join(key_descr_path)):
                cert_path = [addns('KeyInfo', XMLDSIG_NAMESPACE),
                             addns('X509Data', XMLDSIG_NAMESPACE),
                             addns('X509Certificate', XMLDSIG_NAMESPACE)]
                for cert in key_descriptor.findall('/'.join(cert_path)):
                    if 'use' in key_descriptor.attrib:
                        result.append({'use': key_descriptor.attrib['use'],
                                       'text': cert.text})
                    else:
                        result.append({'use': 'signing and encryption',
                                       'text': cert.text})

        collect_certificates_for_role('IDPSSODescriptor')
        collect_certificates_for_role('SPSSODescriptor')

        return result

    @property
    def endpoints(self):
        result = []

        def populate_endpoint(node, endpoint):
            for attr in ('Binding', 'Location'):
                if attr in node.attrib:
                    endpoint[attr] = node.attrib[attr]

        for role, endpoints in {
            'IDPSSODescriptor': [
                'Artifact Resolution Service',
                'Assertion ID Request Service',
                'Manage Name ID Service',
                'Name ID Mapping Service',
                'Single Logout Service',
                'Single Sign On Service',
            ],
            'SPSSODescriptor': [
                'Artifact Resolution Service',
                'Assertion Consumer Service',
                'Manage Name ID Service',
                'Single Logout Service',
                'Request Initiator',
                'Discovery Response',
            ],
        }.items():

            for endpoint in endpoints:
                endpoint_id = endpoint.replace(' ', '')  # remove spaces
                path = [addns(role), addns(endpoint_id)]
                for endpoint_node in self.etree.findall('/'.join(path)):
                    endpoint_aux = {'Type': endpoint}
                    populate_endpoint(endpoint_node, endpoint_aux)
                    result.append(endpoint_aux)

        return result

    @property
    def display_name(self):
        languages = ''
        if self.role_descriptor == 'SP':
            path = [addns('SPSSODescriptor'), addns('Extensions'),
                    addns('UIInfo', MDUI_NAMESPACE),
                    addns('DisplayName', MDUI_NAMESPACE)]
        else:
            path = [addns('IDPSSODescriptor'), addns('Extensions'),
                    addns('UIInfo', MDUI_NAMESPACE),
                    addns('DisplayName', MDUI_NAMESPACE)]
        displays = self.etree.findall('/'.join(path))
        for dn_node in displays:
            lang = getlang(dn_node)
            if lang is None:
                continue  # the lang attribute is required
            if lang == 'en':
                languages = dn_node.text
        if languages == '' and len(displays) > 0:
            languages = displays[0].text
        return languages

    @property
    def geolocationhint(self):
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('GeolocationHint', MDUI_NAMESPACE)]
        result = self.etree.find('/'.join(path))
        if result is not None:
            latitude, longitude = result.text.replace('geo:', '').split(',')
            return {'latitude': latitude, 'longitude': longitude}
        else:
            return None

    @property
    def logos(self):
        languages = {}
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('Logo', MDUI_NAMESPACE)]
        for logo_node in self.etree.findall('/'.join(path)):
            lang = getlang(logo_node)
            if lang is None:
                continue  # the lang attribute is required

            lang_dict = languages.setdefault(lang, {})
            lang_dict['width'] = logo_node.attrib.get('width', '')
            lang_dict['height'] = logo_node.attrib.get('height', '')
            lang_dict['location'] = logo_node.text

        result = []
        for lang, data in languages.items():
            data['lang'] = lang
            result.append(data)

        return result

    @property
    def role_descriptor(self):
        path = [addns('IDPSSODescriptor'), ]
        find_xml = self.etree.find('/'.join(path))
        path2 = [addns('SPSSODescriptor'), ]
        find_xml2 = self.etree.find('/'.join(path2))
        if find_xml is not None and find_xml2 is not None:
            res = 'Both'
        elif find_xml is None:
            res = 'SP'
        else:
            res = 'IDP'
        return res

    @property
    def description(self):
        desc = ''
        if self.role_descriptor == 'SP':
            path = [addns('SPSSODescriptor'), addns('Extensions'),
                    addns('UIInfo', MDUI_NAMESPACE),
                    addns('Description', MDUI_NAMESPACE)]
        else:
            path = [addns('IDPSSODescriptor'), addns('Extensions'),
                    addns('UIInfo', MDUI_NAMESPACE),
                    addns('Description', MDUI_NAMESPACE)]
        find_xml = self.etree.findall('/'.join(path))
        for item in find_xml:
            if item is not None:
                if 'en' in item.values():
                    desc = item.text
        if desc == '' and len(find_xml) > 0:
            desc = find_xml[0].text
        return desc

    @property
    def attributes(self):
        attrs = []
        path = [addns('Extensions'), addns('EntityAttributes', MDATTR_NAMESPACE),
                addns('Attribute', SAML_NAMESPACE)]
        find_xml = self.etree.findall('/'.join(path))
        for node_attr in find_xml:
            if node_attr is not None:
                element = {}
                for items in node_attr.items():
                    element[items[0]] = items[1]
                element['Value'] = node_attr.getchildren()[0].text
                attrs.append(element)
        return attrs


class Entity(models.Model):
    app_label = 'peer.entity'

    class STATE:
        NEW = 'new'
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
        if not hasattr(self, '_parsed_metadata'):
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
                self._parsed_metadata = etree.XML(data)
            except etree.XMLSyntaxError:
                raise ValueError('invalid metadata XML')

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
        except FetchError, e:
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

    @transition(field=state, source='*', target=STATE.MOD)
    def modify(self, temp_metadata):
        self.temp_metadata = temp_metadata

    @transition(field=state, source='*', target=STATE.PUB)
    def approve(self, name, content, username, commit_msg):
        self.temp_metadata = ''
        self.metadata.save(name, content, username, commit_msg)

    @transition(field=state, source=STATE.MOD, target=STATE.PUB)
    def reject(self):
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
