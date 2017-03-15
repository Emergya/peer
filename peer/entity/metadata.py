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
import logging

from django.conf import settings

from peer.entity.utils import NAMESPACES, addns, delns, getlang


logger = logging.getLogger(__name__)

XML_NAMESPACE = NAMESPACES['xml']
XMLDSIG_NAMESPACE = NAMESPACES['ds']
MDUI_NAMESPACE = NAMESPACES['mdui']
MDATTR_NAMESPACE = NAMESPACES['mdattr']
MD_NAMESPACE = NAMESPACES['md']
SAML_NAMESPACE = NAMESPACES['saml']

SP_CATEGORIES = {
    'R&S': 'http://refeds.org/category/research-and-scholarship',
    'CoCo': 'http://www.geant.net/uri/dataprotection-code-of-conduct/v1',
    'R&E': 'http://www.swamid.se/category/research-and-education',
    'SFS': 'http://www.swamid.se/category/sfs-1993-1153',
    'HEI': 'http://www.swamid.se/category/hei-service',
    'NREN': 'http://www.swamid.se/category/nren-service',
    'EU': 'http://www.swamid.se/category/eu-adequate-protection',
}


IDP_CATEGORIES = {
    'R&S': 'http://refeds.org/category/research-and-scholarship',
    'CoCo': 'http://www.geant.net/uri/dataprotection-code-of-conduct/v1',
}

CERTIFICATIONS = {
    'SIRTFI': 'http://refeds.org/sirtfi',
}

MDUI_TR = {
        'display_name': 'DisplayName',
        'description': 'Description',
        'priv_statement_url': 'PrivacyStatementURL',
        'information_url': 'InformationURL',
        'logo': 'Logo',
}


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
        path = [addns('Extensions'),
                addns('EntityAttributes', MDATTR_NAMESPACE),
                addns('Attribute', SAML_NAMESPACE)]
        find_xml = self.etree.findall('/'.join(path))
        for node_attr in find_xml:
            if node_attr is not None:
                element = {}
                for items in node_attr.items():
                    element[items[0]] = items[1]
                children = node_attr.getchildren()
                if len(children):
                    element['Value'] = children[0].text
                attrs.append(element)
        return attrs

    @property
    def security_contact_people(self):
        contact_person_tag = 'md:ContactPerson'
        contact_type_attr = 'remd:contactType'
        path = '//{!s}[@{!s} = "http://refeds.org/metadata/contactType/security"]'
        path = path.format(contact_person_tag, contact_type_attr)
        return self.etree.xpath(path, namespaces=NAMESPACES)

    @property
    def security_contact_email(self):
        people = self.security_contact_people
        email_tag = addns('EmailAddress', NAMESPACES['md'])
        for person in people:
            email_el = person.find(email_tag)
            if email_el is not None:
                email = email_el.text
                if email.startswith('mailto:'):
                    email = email[7:]
                return email

    def _categories(self, attr_name):
        categories = []
        path_segments = ['md:Extensions', 'mdattr:EntityAttributes', 'saml:Attribute']
        path = '/'.join(path_segments)
        xpath = '{!s}[@Name="{!s}"]'.format(path, attr_name)
        find_xml = self.etree.xpath(xpath, namespaces=NAMESPACES)
        if find_xml:
            categories_el = find_xml[0]
            if categories_el is not None:
                for category_el in categories_el.getchildren():
                    categories.append(category_el.text)
        return categories

    @property
    def sp_categories(self):
        attr_name = "http://macedir.org/entity-category"
        return self._categories(attr_name)

    @property
    def idp_categories(self):
        attr_name = "http://macedir.org/entity-category-support"
        return self._categories(attr_name)

    @property
    def certifications(self):
        attr_name = "urn:oasis:names:tc:SAML:attribute:assurance-certification"
        return self._categories(attr_name)

    def _remove_childless_ancestors(self, el):
        while len(el.getchildren()) == 0:
            parent = el.getparent()
            parent.remove(el)
            el = parent

    def _add_categories(self, el, prev, possible, categories):
        for category in categories:
            if category not in prev:
                cat = etree.SubElement(el, addns('AttributeValue', NAMESPACES['saml']))
                cat.text = category

        for category in possible.values():
            if category not in categories:
                path = 'saml:AttributeValue[. = "{!s}"]'.format(category)
                attr_values = el.xpath(path, namespaces=NAMESPACES)
                for val in attr_values:
                    val.getparent().remove(val)
        self._remove_childless_ancestors(el)

    def add_idp_categories(self, idp_categories):
        categories = []
        if idp_categories.research_and_scholarship:
            categories.append(SP_CATEGORIES['R&S'])
        if idp_categories.code_of_conduct:
            categories.append(SP_CATEGORIES['CoCo'])
            self.add_mdui_info_piece('PrivacyStatementURL',
                    idp_categories.coc_priv_statement_url,
                    idp_categories.lang_priv_statement_url)
        if idp_categories.sirtfi_id_assurance:
            self.add_sirtfi_id_assurance()
            self.add_security_contact_person(idp_categories.security_contact_email)
        else:
            self.rm_sirtfi_id_assurance()
        categories_el = self.get_or_create_categories_support_el()
        categories_prev = self.idp_categories
        self._add_categories(categories_el, categories_prev,
                IDP_CATEGORIES, categories)

    def add_sp_categories(self, sp_categories):
        categories = []
        if sp_categories.research_and_scholarship:
            categories.append(SP_CATEGORIES['R&S'])
        if sp_categories.code_of_conduct:
            categories.append(SP_CATEGORIES['CoCo'])
            self.add_mdui_info_piece('PrivacyStatementURL',
                    sp_categories.coc_priv_statement_url,
                    sp_categories.lang_priv_statement_url)
        if sp_categories.research_and_education:
            categories.append(SP_CATEGORIES['R&E'])
            if sp_categories.rae_hei_service:
                categories.append(SP_CATEGORIES['HEI'])
            if sp_categories.rae_nren_service:
                categories.append(SP_CATEGORIES['NREN'])
            if sp_categories.rae_eu_protection:
                categories.append(SP_CATEGORIES['EU'])
        if sp_categories.swamid_sfs:
            categories.append(SP_CATEGORIES['SFS'])
        if sp_categories.sirtfi_id_assurance:
            self.add_sirtfi_id_assurance()
            self.add_security_contact_person(sp_categories.security_contact_email)
        else:
            self.rm_sirtfi_id_assurance()
        categories_el = self.get_or_create_categories_el()
        categories_prev = self.sp_categories
        self._add_categories(categories_el, categories_prev,
                SP_CATEGORIES, categories)

    def get_or_create_entity_extensions_el(self):
        extensions_tag = addns('Extensions', NAMESPACES['md'])
        extensions_el = self.etree.find(extensions_tag)
        if extensions_el is None:
            extensions_el = etree.Element(extensions_tag)
            self.etree.insert(0, extensions_el)
        return extensions_el

    def get_or_create_descriptor_extensions_el(self):
        if self.role_descriptor == 'SP':
            descriptor_tag = addns('SPSSODescriptor')
        else:
            descriptor_tag = addns('IDPSSODescriptor')
        descriptor_el = self.etree.find('.//{!s}'.format(descriptor_tag))
        extensions_tag = addns('Extensions', NAMESPACES['md'])
        extensions_el = descriptor_el.find(extensions_tag)
        if extensions_el is None:
            extensions_el = etree.Element(extensions_tag)
            descriptor_el.insert(0, extensions_el)
        return extensions_el

    def get_or_create_entity_attrs_el(self):
        extensions_el = self.get_or_create_entity_extensions_el()
        entity_attrs = addns('EntityAttributes', NAMESPACES['mdattr'])
        entity_attrs_el = extensions_el.find(entity_attrs)
        if entity_attrs_el is None:
            entity_attrs_el = etree.SubElement(extensions_el, entity_attrs)
        return entity_attrs_el

    def _get_or_create_categories_el(self, attr_name):
        entity_attrs_el = self.get_or_create_entity_attrs_el()
        path = 'saml:Attribute[@Name="{!s}"]'.format(attr_name)
        categories_attr_els = entity_attrs_el.xpath(path, namespaces=NAMESPACES)
        if not categories_attr_els:
            NSMAP = {None: NAMESPACES['saml']}
            categories_attr_el = etree.SubElement(entity_attrs_el,
                    addns('Attribute', NAMESPACES['saml']),
                    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                    Name=attr_name,
                    nsmap=NSMAP)
        else:
            categories_attr_el = categories_attr_els[0]
        return categories_attr_el

    def get_or_create_categories_el(self):
        attr_name = "http://macedir.org/entity-category"
        return self._get_or_create_categories_el(attr_name)

    def get_or_create_categories_support_el(self):
        attr_name = "http://macedir.org/entity-category-support"
        return self._get_or_create_categories_el(attr_name)

    def get_or_create_assurance_certification_el(self):
        attr_name = "urn:oasis:names:tc:SAML:attribute:assurance-certification"
        return self._get_or_create_categories_el(attr_name)

    def _has_categories_el(self, attr_name):
        extensions_tag = addns('Extensions', NAMESPACES['md'])
        extensions_el = self.etree.find(extensions_tag)
        if extensions_el is None:
            return False
        entity_attrs = addns('EntityAttributes', NAMESPACES['mdattr'])
        entity_attrs_el = extensions_el.find(entity_attrs)
        if entity_attrs_el is None:
            return False
        path = 'saml:Attribute[@Name="{!s}"]'.format(attr_name)
        categories_attr_el = entity_attrs_el.xpath(path, namespaces=NAMESPACES)
        if not categories_attr_el:
            return False
        return True

    def has_categories_el(self):
        attr_name = "http://macedir.org/entity-category"
        return self._has_categories_el(attr_name)

    def has_categories_support_el(self):
        attr_name = "http://macedir.org/entity-category-support"
        return self._has_categories_el(attr_name)

    def has_assurance_certification_el(self):
        attr_name = "urn:oasis:names:tc:SAML:attribute:assurance-certification"
        return self._has_categories_el(attr_name)

    def has_uiinfo_el(self):
        extensions_el = self.get_or_create_descriptor_extensions_el()
        uiinfo_tag = addns('UIInfo', NAMESPACES['mdui'])
        uiinfo_el = extensions_el.find(uiinfo_tag)
        if uiinfo_el is None:
            return False
        return  True

    def get_or_create_uiinfo_el(self):
        extensions_el = self.get_or_create_descriptor_extensions_el()
        uiinfo_tag = addns('UIInfo', NAMESPACES['mdui'])
        uiinfo_el = extensions_el.find(uiinfo_tag)
        if uiinfo_el is None:
            uiinfo_el = etree.SubElement(extensions_el, uiinfo_tag)
        return  uiinfo_el

    def add_sirtfi_id_assurance(self):
        certification_el = self.get_or_create_assurance_certification_el()
        for child in certification_el.getchildren():
            if child.text == CERTIFICATIONS['SIRTFI']:
                break
        else:
            sirtfi = etree.SubElement(certification_el,
                        addns('AttributeValue', NAMESPACES['saml']))
            sirtfi.text = CERTIFICATIONS['SIRTFI']

    def rm_sirtfi_id_assurance(self):
        certification_el = self.get_or_create_assurance_certification_el()
        for child in certification_el.getchildren():
            if child.text == CERTIFICATIONS['SIRTFI']:
                certification_el.remove(child)
        self._remove_childless_ancestors(certification_el)

    def add_security_contact_person(self, email):
        if email == self.security_contact_email:
            return
        NSMAP = {
                None: NAMESPACES['md'],
                'remd': NAMESPACES['remd']
                }
        contact_person_tag = addns('ContactPerson', NAMESPACES['md'])
        contact_type_attr = addns('contactType', NAMESPACES['remd'])
        people = self.security_contact_people
        if len(people):
            contact_person_el = people[0]
        else:
            contact_person_el = etree.Element(contact_person_tag, **{
                contact_type_attr: 'http://refeds.org/metadata/contactType/security',
                'contactType': 'other',
                'nsmap': NSMAP
                })
        email_tag = addns('EmailAddress', NAMESPACES['md'])
        email_el = contact_person_el.find(email_tag)
        if email_el is None:
            email_el = etree.SubElement(contact_person_el, email_tag)
        email_el.text = 'mailto:{!s}'.format(email)
        self.etree.append(contact_person_el)
        return contact_person_el

    def get_mdui_info_piece(self, tag, lang):
        uiinfo_el = self.get_or_create_uiinfo_el()
        lang_attr = 'xml:lang'
        xpath_tag = 'mdui:' + tag
        path = '{!s}[@{!s}="{!s}"]'.format(xpath_tag, lang_attr, lang)
        elements = uiinfo_el.xpath(path, namespaces=NAMESPACES)
        if len(elements):
            return elements[0]

    def add_mdui_info_piece(self, tag, data, lang):
        mdui_piece_el = self.get_mdui_info_piece(tag, lang)
        if mdui_piece_el is not None:
            mdui_piece_el.text = data
            return
        uiinfo_el = self.get_or_create_uiinfo_el()
        xml_tag = addns(tag, NAMESPACES['mdui'])
        lang_attr = addns('lang', NAMESPACES['xml'])
        element = etree.SubElement(uiinfo_el, xml_tag, **{
            lang_attr: lang
            })
        element.text = data
        return element

    def add_mdui_logo(self, data, lang, height, width):
        tag = 'Logo'
        logo_el = self.get_mdui_info_piece(tag, lang)
        if logo_el is not None:
            logo_el.text = data
            logo_el.attrib['height'] = height
            logo_el.attrib['width'] = width
            return
        uiinfo_el = self.get_or_create_uiinfo_el()
        xml_tag = addns(tag, NAMESPACES['mdui'])
        lang_attr = addns('lang', NAMESPACES['xml'])
        element = etree.SubElement(uiinfo_el, xml_tag, **{
            lang_attr: lang,
            'height': height,
            'width': width,
            })
        element.text = data
        return element

    def rm_mdui_info_piece(self, tag, lang):
        uiinfo_el = self.get_or_create_uiinfo_el()
        element = self.get_mdui_info_piece(tag, lang)
        if element is not None:
            uiinfo_el.remove(element)

    @property
    def privacy_statement_url(self):
        uiinfo_el = self.get_or_create_uiinfo_el()
        lang_attr = 'xml:lang'
        xpath_tag = 'mdui:PrivacyStatementURL'
        for language in settings.MDUI_LANGS:
            lang = language[0]
            path = '{!s}[@{!s}="{!s}"]'.format(xpath_tag, lang_attr, lang)
            elements = uiinfo_el.xpath(path, namespaces=NAMESPACES)
            if len(elements):
                return lang, elements[0]

    def add_mdui(self, mdui):
        lang = mdui.lang
        for piece in MDUI_TR:
            tag = MDUI_TR[piece]
            data = getattr(mdui, piece, False)
            if data not in (False, None):
                if piece == 'logo':
                    self.add_mdui_logo(data, lang,
                            str(mdui.logo_height), str(mdui.logo_width))
                else:
                    self.add_mdui_info_piece(tag, data, lang)
            else:
                self.rm_mdui_info_piece(tag, lang)
        uiinfo_el = self.get_or_create_uiinfo_el()
        self._remove_childless_ancestors(uiinfo_el)

    def get_contact_people(self, type):
        from peer.entity.models import ContactPerson
        type = dict(ContactPerson.CONTACT_TYPES)[type]
        contact_person_tag = 'md:ContactPerson'
        contact_type_attr = 'contactType'
        path = '//{!s}[@{!s} = "{!s}"]'
        path = path.format(contact_person_tag, contact_type_attr, type)
        return self.etree.xpath(path, namespaces=NAMESPACES)

    def add_contact_person(self, type):
        NSMAP = {
                None: NAMESPACES['md'],
                }
        contact_person_tag = addns('ContactPerson', NAMESPACES['md'])
        contact_person_el = etree.Element(contact_person_tag, **{
            'contactType': type,
            'nsmap': NSMAP
            })
        self.etree.append(contact_person_el)
        return contact_person_el

    def get_contact_data(self, tag, type):
        for contact in self.get_contact_people(type):
            element = contact.find(addns(tag))
            if element is not None:
                return element.text

    def add_contact(self, contact):
        contacts = self.get_contact_people(contact.type)
        if len(contacts):
            contact_el = contacts[0]
        else:
            contact_el = self.add_contact_person(contact.type)
        if contact.email:
            email_tag = addns('EmailAddress', NAMESPACES['md'])
            email_el = contact_el.find(email_tag)
            if email_el is None:
                email_el = etree.SubElement(contact_el, email_tag)
            email_el.text = 'mailto:{!s}'.format(contact.email)
        if contact.name:
            name_tag = addns('SurName', NAMESPACES['md'])
            name_el = contact_el.find(name_tag)
            if name_el is None:
                name_el = etree.SubElement(contact_el, name_tag)
            name_el.text = contact.name
        if contact.phone:
            phone_tag = addns('TelephoneNumber', NAMESPACES['md'])
            phone_el = contact_el.find(phone_tag)
            if phone_el is None:
                phone_el = etree.SubElement(contact_el, phone_tag)
            phone_el.text = contact.phone
        return contact_el
