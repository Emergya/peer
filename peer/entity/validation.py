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

from lxml import etree
import urlparse

from django.conf import settings
from django.utils.importlib import import_module

from peer.entity.models import Metadata, EntityMD
from peer.entity.utils import NAMESPACES, expand_settings_permissions
from peer.entity.utils import compare_elements, load_schema
from peer.domain.validation import check_superdomain_verified


def validate(entity, doc, user=None):
    """
    Call all validators defined in in settings.METADATA_VALIDATORS
    on the xml given as a string (doc). Information about the
    entity this metadata is validating for is passed in the first
    argument (entity).

    Each entry in METADATA_VALIDATORS is a string with the import path
    to a callable that accepts a string as input and returns a list
    of strings describing errors, or an empty list on no errors.
    """
    try:
        validators = settings.METADATA_VALIDATORS
    except AttributeError:
        validators = []
    errors = set()
    for v in validators:
        val_list = v.split('.')
        mname = '.'.join(val_list[:-1])
        cname = val_list[-1]
        module = import_module(mname)
        validator = getattr(module, cname)
        errors.update(validator(entity, doc, user=user))
    return list(errors)


def _parse_metadata(doc):
    """Aux function that returns a list of errors and a metadata object"""
    if type(doc) == unicode:
        doc = doc.encode('utf-8', 'ignore')
    try:
        metadata = Metadata(etree.XML(doc))
    except etree.XMLSyntaxError, e:
        # XXX sin traducir (como traducimos e.msg?)
        error = e.msg or 'Unknown error, perhaps an empty doc?'
        return [u'XML syntax error: ' + error], None
    else:
        return [], metadata


def validate_xml_syntax(entity, doc, user=None):
    """
    Check that the provided string contains syntactically valid xml,
    simply by trying to parse it with lxml.
    """
    return _parse_metadata(doc)[0]


def validate_domain_in_endpoints(entity, doc, user=None):
    """
    Makes sure the endpoints urls belongs to the domain of the entity
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    domain = entity.domain.name
    if user is None:
        user = entity.domain.owner

    for endpoint in metadata.endpoints:
        if 'Location' in endpoint:
            url = urlparse.urlparse(endpoint['Location'])
            if not check_superdomain_verified(url.hostname.lower(), user=user):
                errors.append(
                    u'The endpoint at %s does not belong to the domain %s'
                    u' or to any of its subdomains.' %
                    (endpoint['Location'], domain))

    return errors


def validate_domain_in_entityid(entity, doc, user=None):
    """
    Makes sure the entityid url belongs to the domain of the entity
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    domain = entity.domain.name
    if user is None:
        user = entity.domain.owner

    url = urlparse.urlparse(metadata.entityid)
    if not check_superdomain_verified(url.netloc.lower(), user=user):
        errors.append(
            u'The entityid does not belong to the domain %s'
            u' or to any of its subdomains.' % domain)

    return errors


def validate_metadata_permissions(entity, doc, user=None):
    """
    Checks whether the user has permission to change an element metadata of
    an entity.
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    new_etree = metadata.etree
    old_etree = entity.metadata_etree

    if old_etree == new_etree:
        return errors

    permissions = expand_settings_permissions()
    if not permissions:
        return errors

    for xpath, perm, desc in permissions:
        if old_etree is not None:
            old_elems = old_etree.xpath(xpath, namespaces=NAMESPACES)
        else:
            old_elems = list()
        new_elems = new_etree.xpath(xpath, namespaces=NAMESPACES)

        # Element addition
        if len(old_elems) < len(new_elems) and \
                perm.startswith('add') and \
                not user.has_perm('.'.join(('entity', perm))):
            errors.append(u'Addition is forbidden in element %s' %
                          (new_elems[0].tag))

        # Element deletion
        elif len(old_elems) > len(new_elems) and \
                perm.startswith('delete') and \
                not user.has_perm('.'.join(('entity', perm))):
            errors.append(u'Deletion is forbidden in element %s' %
                          (new_elems[0].tag))

        # Element modification
        elif (old_elems and new_elems) and \
                (len(old_elems) == len(new_elems)) and \
                perm.startswith('modify') and \
                not user.has_perm('.'.join(('entity', perm))):
            for old_elem, new_elem in zip(old_elems, new_elems):
                if not compare_elements(old_elem, new_elem):
                    errors.append(
                        u'Value modification is forbidden for element %s' %
                        (new_elem.tag))
                    break
    return errors


def validate_schema(entity, doc, user=None):
    """
    Makes sure the the entity is correct regarding the XML Schema.
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    schema = load_schema()
    if not schema.validate(metadata.etree):
        for error in schema.error_log:
            if error.type_name != "SCHEMAP_WARN_SKIP_SCHEMA":
                errors.append(unicode(error))

    return errors


def validate_unique_entityid(entity, doc, user=None):
    """
    Makes sure the entityid url belongs to the domain of the entity
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    entityid = metadata.etree.attrib['entityID']
    prev = EntityMD.objects.filter(entityid=entityid)
    if entity.pk is not None:
        prev = prev.exclude(pk=entity.pk)
    if prev.count() > 0:
        errors.append(
            u'There is already an en entity with the'
            u' provided EntityID: %s' % entityid)

    return errors
