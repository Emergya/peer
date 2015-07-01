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

from itertools import islice

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from pygments import highlight
from pygments.lexers import DiffLexer, XmlLexer
from pygments.formatters import HtmlFormatter

from peer.account.templatetags.account import authorname
from peer.entity.models import Entity
from peer.entity.utils import add_previous_revisions


class EntitiesFeed(Feed):

    title = _(u'Entities')
    description = _(u'Full list of entities')

    def get_object(self, request):
        self.request = request

    def link(self):
        return reverse('entities:entities_feed')

    def items(self):
        if not self.request.GET:
            entities = Entity.objects.all()
        else:
            queries = self.request.GET.getlist('xpath')
            entities = Entity.objects.xpath_filters(queries)

        try:
            return islice(entities, 0,
                          settings.MAX_FEED_ENTRIES)
        except AttributeError:
            return entities

    def item_title(self, item):
        return unicode(item)

    def item_description(self, item):
        if item.metadata:
            formatter = HtmlFormatter(linenos=False,
                                      outencoding=settings.DEFAULT_CHARSET)
            if item.has_metadata():
                xml = item.metadata.read()
                return highlight(xml, XmlLexer(), formatter)
            else:
                return ugettext(u'No metadata yet')

    def item_link(self, item):
        return item.get_absolute_url()


class ChangesFeed(Feed):

    def get_object(self, request, entity_id):
        return get_object_or_404(Entity, pk=entity_id)

    def title(self, entity):
        return (ugettext(u'Changes on the metadata of entity %s')
                % unicode(entity))

    def link(self, entity):
        return reverse('entities:entity_view', args=(entity.id,))

    def description(self, entity):
        return (ugettext(u'Recent changes made on the metadata of entity %s')
                % unicode(entity))

    def author_name(self, entity):
        return authorname(entity.owner)

    def author_email(self, entity):
        return entity.owner.email

    def items(self, entity):
        revs = add_previous_revisions(entity.metadata.list_revisions())
        return [{'entity': entity, 'revision': rev} for rev in revs]

    def item_title(self, item):
        return u'%s - %s' % (item['revision']['versionid'],
                             item['revision']['message'])

    def item_description(self, item):
        entity = item['entity']
        current = item['revision']['versionid']
        formatter = HtmlFormatter(linenos=True,
                                  outencoding=settings.DEFAULT_CHARSET)
        if 'previous' in item['revision']:
            previous = item['revision']['previous']
            diff = entity.metadata.get_diff(previous, current)
            html = highlight(diff, DiffLexer(), formatter)
        else:
            xml = entity.metadata.get_revision(current)
            html = highlight(xml, XmlLexer(), formatter)

        return html

    def item_link(self, item):
        return reverse('entities:get_revision', args=[item['entity'].id,
                                             item['revision']['versionid']])

    def item_author_name(self, item):
        return item['revision']['author']

    def item_pubdate(self, item):
        return item['revision']['date']
