# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
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
import urlparse
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from peer.customfields import SafeCharField
from peer.domain.utils import generate_validation_key


class Domain(models.Model):
    name = SafeCharField(_(u'Domain name'), max_length=100, unique=True)
    owner = models.ForeignKey(User, verbose_name=_('Identified domain owner'),
                              blank=True, null=True)
    validated = models.BooleanField(
        _(u'Validated'), default=False,
        help_text=_(u'Used to know if the owner actual owns the domain'))
    validation_key = models.CharField(_('Domain validation key'),
                                      max_length=100, blank=True, null=True)
    team = models.ManyToManyField(User, verbose_name=_('Team'),
                                  related_name='team_domains',
                                  through='DomainTeamMembership')
    moderators = models.ManyToManyField(User, verbose_name=_('Reviewers'),
                                        related_name='moderator_team_domains',
                                        through='DomainModeratorsTeamMembership')

    @property
    def validation_url(self):
        domain = u'http://%s' % self.name
        return urlparse.urljoin(domain, self.validation_key)

    @property
    def validation_url_with_www_prefix(self):
        if not self.name.startswith(u'www'):
            domain = u'http://www.%s' % self.name
            return urlparse.urljoin(domain, self.validation_key)

    @property
    def validation_secure_url(self):
        domain = u'https://%s' % self.name
        return urlparse.urljoin(domain, self.validation_key)

    @property
    def validation_secure_url_with_www_prefix(self):
        if not self.name.startswith(u'www'):
            domain = u'https://www.%s' % self.name
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


class DomainTeamMembership(models.Model):
    domain = models.ForeignKey(Domain, verbose_name=_(u'Domain'))
    member = models.ForeignKey(User, verbose_name=_('Member'),
                               related_name='domain_teams')
    date = models.DateTimeField(_(u'Membership date'),
                                default=datetime.now)

    class Meta:
        verbose_name = _(u'Domain team membership')
        verbose_name_plural = _(u'Domain team memberships')

    def __unicode__(self):
        return ugettext(
            u'%(user)s can create entities with domain %(domain)s') % {
            'user': self.member.username, 'domain': self.domain.name}


class DomainModeratorsTeamMembership(models.Model):
    domain = models.ForeignKey(Domain, verbose_name=_(u'Domain'))
    member = models.ForeignKey(User, verbose_name=_('Member'),
                               related_name='domain_moderator_teams')
    date = models.DateTimeField(_(u'Membership date'),
                                default=datetime.now)

    class Meta:
        verbose_name = _(u'Domain moderator team membership')
        verbose_name_plural = _(u'Domain moderator team memberships')

    def __unicode__(self):
        return ugettext(
            u'%(user)s can moderate entities with domain %(domain)s') % {
            'user': self.member.username, 'domain': self.domain.name}


class DomainToken(models.Model):
    domain = models.CharField(_(u'Domain name'), max_length=100)
    token = models.CharField(_(u'Token'), unique=True, max_length=100)

    class Meta:
        verbose_name = _(u'Domain token')
        verbose_name_plural = _(u'Domain tokens')

    def __unicode__(self):
        return u'%s  -  %s' % (self.domain, self.token)
