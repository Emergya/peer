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


from django.conf import settings
from django.core.paginator import Paginator, Page, InvalidPage, EmptyPage
from json import dumps


class EntitiesPaginator(Paginator):

    def page(self, number):
        plain_page = super(EntitiesPaginator, self).page(number)
        return EntitiesPage(plain_page.object_list, plain_page.number,
                            plain_page.paginator)


class EntitiesPage(Page):

    def __init__(self, object_list, number, paginator):
        super(EntitiesPage, self).__init__(object_list, number, paginator)

        self.geo_list = []
        for entity in object_list:
            if entity.has_metadata() and entity.geolocationhint:
                self.geo_list.append({
                    'entity': unicode(entity),
                    'geolocationhint': entity.geolocationhint
                })

    def has_geoinfo(self):
        return len(self.geo_list) > 0

    def geoinfo(self):
        return self.geo_list

    def geoinfo_as_json(self):
        return dumps(self.geo_list)


def get_entities_per_page():
    if hasattr(settings, 'ENTITIES_PER_PAGE'):
        return settings.ENTITIES_PER_PAGE
    else:
        return 10


def paginated_list_of_entities(request, entities):
    paginator = EntitiesPaginator(entities, get_entities_per_page())

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        entities = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entities = paginator.page(paginator.num_pages)
    return entities
