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

import logging
import urllib2
from tempfile import NamedTemporaryFile

from lxml import etree
import pkg_resources

from django.conf import settings
from django.core.files.base import File
from django.contrib.auth.models import User


logger = logging.getLogger('peer.utils')


NAMESPACES = {
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xs': 'xs="http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'md': 'urn:oasis:names:tc:SAML:2.0:metadata',
    'mdui': 'urn:oasis:names:tc:SAML:metadata:ui',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
    'mdattr': 'urn:oasis:names:tc:SAML:metadata:attribute',
}

SAML_METADATA_NAMESPACE = NAMESPACES['md']

CONNECTION_TIMEOUT = 10


def addns(node_name, namespace=SAML_METADATA_NAMESPACE):
    '''Return a node name qualified with the XML namespace'''
    return '{' + namespace + '}' + node_name


def delns(node, namespace=SAML_METADATA_NAMESPACE):
    return node.replace('{' + namespace + '}', '')


def getlang(node):
    if 'lang' in node.attrib:
        return node.attrib['lang']
    elif addns('lang', NAMESPACES['xml']) in node.attrib:
        return node.attrib[addns('lang', NAMESPACES['xml'])]


def add_previous_revisions(revisions):
    prev, revs = '', []
    for rev in revisions[::-1]:
        if prev:
            rev['previous'] = prev
        prev = rev['versionid']
        revs.append(rev)
    return reversed(revs)


def expand_settings_permissions(include_xpath=True):
    permissions = []

    if hasattr(settings, 'METADATA_PERMISSIONS'):
        perm_setts = settings.METADATA_PERMISSIONS
        for prefix in ('add', 'delete', 'modify'):
            for xpath, name, desc in perm_setts:
                perm_class = '_'.join((prefix, name))
                perm_desc = ' '.join(('Can', prefix.capitalize(), desc))
                exp_perms = [perm_class, perm_desc]
                if include_xpath:
                    exp_perms.insert(0, xpath)
                permissions.append(tuple(exp_perms))

    return tuple(permissions)


def safe_split(text, split_chars=' ',
               start_protected_chars='[', end_protected_chars=']'):
    """Safely split text even in split_chars are inside protected regions.

    Protected regions starts with any character from the start_protected_chars
    argument and ends with any character from the end_protected_chars argument.

    If a char from split_chars is found inside a protected region it will be
    ignored and the text will not be splited at that position.
    """
    parts = []
    inside_protected_region = False
    last_part = []
    for char in text:
        if char in start_protected_chars:
            inside_protected_region = True

        if char in end_protected_chars:
            inside_protected_region = False

        if char in split_chars:
            if inside_protected_region:
                last_part.append(char)
            else:
                parts.append(u''.join(last_part))
                last_part = []

        else:
            last_part.append(char)

    if last_part:
        parts.append(u''.join(last_part))

    return parts


class FetchError(Exception):
    pass


def fetch_resource(url, decode=True):
    try:
        resp = urllib2.urlopen(url, None, CONNECTION_TIMEOUT)
    except urllib2.URLError, e:
        raise FetchError('URL Error: ' + str(e))
    except urllib2.HTTPError, e:
        raise FetchError('HTTP Error: ' + str(e))
    except:
        return None

    if resp.getcode() != 200:
        raise FetchError('Error in the response: %d' % resp.getcode())

    text = resp.read()
    if decode:
        try:
            encoding = resp.headers['content-type'].split('charset=')[1]
            text = text.decode(encoding)
        except (KeyError, IndexError):
            pass
    resp.close()
    return text


def write_temp_file(text, encoding='utf-8', delete=True):
    tmp = NamedTemporaryFile(delete=delete)
    if type(text) == unicode:
        text = text.encode(encoding, 'ignore')
    tmp.write(text)
    tmp.seek(0)
    return File(tmp)


def is_subscribed(entity, user):
    try:
        entity.subscribers.get(id=user.id)
        return True
    except User.DoesNotExist:
        return False


def add_subscriber(entity, user):
    if not is_subscribed(entity, user):
        entity.subscribers.add(user)


def remove_subscriber(entity, user):
    if is_subscribed(entity, user):
        entity.subscribers.remove(user)


def strip_entities_descriptor(metadata_text):
    """Strip off the EntitiesDescriptor element from the metadata_text.

    If the metadata's root node is EntityDescriptor it will be left
    untouched. Otherwise (the root node is EntitiesDescriptor), it will
    remove the root node and the child will be the new root node.

    If the root node is an EntitiesDescriptor and there are more than one
    EntityDescriptor, it will raise a ValueError.
    """
    result = metadata_text
    if result:
        try:
            if type(result) == unicode:
                result = result.encode('utf-8')
            root = etree.XML(result)
            if addns('EntitiesDescriptor') == root.tag:
                children = root.getchildren()
                if len(children) != 1:
                    raise ValueError("The metadata must have just one EntityDescriptor")
                else:
                    result = etree.tostring(children[0])
        except etree.XMLSyntaxError as e:
            raise ValueError("Invalid XML Syntax: %s" % e.msg)

    return result


def compare_elements(element1, element2):
    """Return True if both elements are equivalent. False otherwise"""
    if element1.tag != element2.tag:
        return False

    if element1.keys() != element2.keys():
        return False

    if element1.values() != element2.values():
        return False

    if element1.text != element2.text:
        return False

    return True


class ResourceResolver(etree.Resolver):

    def resolve(self, system_url, public_id, context):
        """
        Resolves URIs using the resource API
        """
        logger.debug("resolve SYSTEM URL' %s' for '%s'" % (system_url, public_id))
        path = system_url.split("/")
        fn = path[len(path) - 1]
        if pkg_resources.resource_exists(__name__, fn):
            return self.resolve_file(pkg_resources.resource_stream(__name__, fn), context)
        elif pkg_resources.resource_exists(__name__, "schema/%s" % fn):
            return self.resolve_file(pkg_resources.resource_stream(__name__, "schema/%s" % fn), context)
        else:
            raise ValueError("Unable to locate %s" % fn)


def load_schema():
    """
    Returns an etree.XMLSchema object with the contents of schema/schema.xsd
    """
    schema = None
    try:
        parser = etree.XMLParser()
        parser.resolvers.add(ResourceResolver())
        schema_stream = pkg_resources.resource_stream(__name__, "schema/schema.xsd")
        st = etree.parse(schema_stream, parser)
        schema = etree.XMLSchema(st)
    except etree.XMLSchemaParseError, ex:
        error_lines = ["%s" % e for e in ex.error_log if ":WARNING:" not in e]
        logger.error('\n'.join(error_lines))
        raise ex

    return schema
