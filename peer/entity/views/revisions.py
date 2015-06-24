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

from pygments import highlight
from pygments.lexers import XmlLexer, DiffLexer
from pygments.formatters import HtmlFormatter

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page

from peer.entity.models import Entity


# ENTITY DETAILS

HTML_WRAPPER = u'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>%s - %s</title>
</head>
<body>
%s
</body>
</html>
'''


def get_diff(request, entity_id, r1, r2):
    entity = get_object_or_404(Entity, id=entity_id)
    diff = entity.metadata.get_diff(r1, r2)
    formatter = HtmlFormatter(linenos=True)
    html = HTML_WRAPPER % (entity_id, u'%s:%s' % (r1, r2),
                           highlight(diff, DiffLexer(), formatter))
    return HttpResponse(html.encode(settings.DEFAULT_CHARSET))


def get_revision(request, entity_id, rev):
    entity = get_object_or_404(Entity, id=entity_id)
    md = entity.metadata.get_revision(rev)
    formatter = HtmlFormatter(linenos=True)
    html = HTML_WRAPPER % (entity_id, rev,
                           highlight(md, XmlLexer(), formatter))
    return HttpResponse(html.encode(settings.DEFAULT_CHARSET))


def get_latest_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    metadata_text = entity.metadata.get_revision()
    return HttpResponse(metadata_text,
                        content_type="application/samlmetadata+xml")


@cache_page(60 * 60 * 24)
def get_pygments_css(request):
    formatter = HtmlFormatter(linenos=True, outencoding='utf-8')
    return HttpResponse(
        content=formatter.get_style_defs(arg=''),
        content_type='text/css; charset=' + settings.DEFAULT_CHARSET,
    )
