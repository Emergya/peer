# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from domain.validation import generate_validation_key


class Domain(models.Model):

    name = models.CharField(_(u'Domain name'), max_length=100, unique=True)
    owner = models.ForeignKey(User, verbose_name=_('Identified domain owner'),
                              blank=True, null=True)
    validated = models.BooleanField(
        _(u'Validated'), default=False,
        help_text=_(u'Used to know if the owner actual owns the domain'))
    validation_key = models.CharField(_('Domain validation key'),
                                      max_length=100, blank=True, null=True)

    @property
    def validation_url(self):
        domain = 'http://%s' % self.name
        return urlparse.urljoin(domain, self.validation_key)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Domain')
        verbose_name_plural = _(u'Domains')


def pre_save_handler(sender, instance, **kwargs):
    if not instance.validation_key:
        instance.validation_key = generate_validation_key(
            instance.name,
            instance.owner and instance.owner.username)
        instance.save()

signals.post_save.connect(pre_save_handler, sender=Domain)