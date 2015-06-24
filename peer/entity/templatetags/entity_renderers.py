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

from django import template

register = template.Library()



@register.inclusion_tag('entity/list_item.html')
def render_entity_as_list_item(entity, moderation_enabled):
    has_metadata = entity.has_metadata()

    state = None
    if has_metadata and entity.state:
        state = entity.state

    organization = None
    if has_metadata and entity.organization:
        for l18n in entity.organization:
            organization = l18n
            break

    valid_until = None
    if has_metadata and entity.valid_until:
        valid_until = entity.valid_until

    endpoints = 0
    if has_metadata:
        endpoints = len(entity.endpoints)

    contacts = 0
    if has_metadata:
        contacts = len(entity.contacts)

    certificates = 0
    if has_metadata:
        certificates = len(entity.certificates)

    return {
        'entity': entity,
        'state': state,
        'has_metadata': has_metadata,
        'organization': organization,
        'valid_until': valid_until,
        'endpoints': endpoints,
        'contacts': contacts,
        'certificates': certificates,
        'moderation_enabled': moderation_enabled,
    }


@register.filter
def truncatechars(value, length):
    if length < len(value):
        return value[0:int(length)] + u'...'
    else:
        return value


@register.filter
def letterwrap(value, length):
    result = []
    data = str(value)  # make a copy
    while data:
        size = min(length, len(data))
        result.append(data[:size])
        data = data[size:]

    return '\n'.join(result)
