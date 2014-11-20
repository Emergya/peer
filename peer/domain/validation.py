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


import httplib
import urllib2
import whois
from whois.parser import PywhoisError
import dns.resolver
from dns.resolver import NXDOMAIN
from dns.exception import DNSException, Timeout
from publicsuffix import PublicSuffixList

from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from peer.domain.models import DomainToken, Domain
from peer.domain.utils import get_custom_user_agent, SmartRedirectHandler


CONNECTION_TIMEOUT = 10


def http_validate_ownership(validation_url, validation_code, timeout=CONNECTION_TIMEOUT):
    """ True if the validation_url exists returning a 200 status code and
        the file contains the validation_code.
    False otherwise
    """
    if not validation_url:
        return False

    valid = False
    try:
        request = urllib2.Request(validation_url)
        custom_user_agent = get_custom_user_agent()
        if custom_user_agent:
            request.addheaders = [('User-agent', custom_user_agent)]
        # To avoid redirections
        opener = urllib2.build_opener(SmartRedirectHandler())
        response = opener.open(request, None, timeout)
    except (urllib2.URLError, httplib.BadStatusLine):
        return False

    if response.getcode() == 200 and not hasattr(response, 'redirection'):
        search_string = 'validation-code=%s' % validation_code
        content = response.read()
        if search_string in content:
            valid = True
    response.close()
    return valid


def dns_validate_ownership(domain, validation_record, timeout=CONNECTION_TIMEOUT, request=None):
    """ True if validation_record is in any of the DNS TXT records.

    False otherwise
    """
    if not validation_record:
        return False

    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    try:
        answers = resolver.query(domain, 'TXT')
    except NXDOMAIN:
        if request:
            messages.error(
                request, _(u'Error DNS validation: Domain %s not found' % domain))
        return False
    except Timeout:
        messages.error(
            request, _(u'Error DNS validation: Timeout'))
        return False
    # All DNS exceptions subclass from this one
    except DNSException:
        # Check for TXT in root domain
        segs = domain.split('.')
        if len(segs) > 2:
            root_domain = '.'.join(segs[-2:])
            dns_validate_ownership(root_domain, validation_record)
        return False

    if not answers:
        messages.error(
            request, _(u'Error DNS validation: Zone file does not contain a TXT record'))
    else:
        for ans in answers:
            if ans.to_text().strip('\"') == validation_record:
                return True
    messages.error(
        request, _(u'Error DNS validation: The required TXT record was not found'))
    return False


def email_validate_ownership(domain_name, token):
    """ Checks if the given token matchs an entry of the database, that token
        was provided in an email """
    return check_domain_token(domain_name, token)


def check_domain_token(domain_name, token):
    """ True if exists an entry in the database with the domain_name and the token

    False otherwise
    """
    valid_token = DomainToken.objects.filter(domain=domain_name, token=token).exists()
    if valid_token:
        DomainToken.objects.filter(domain=domain_name).delete()
    return valid_token


def check_superdomain_verified(domain):
    '''
    True if some superdomain of the given domain is already
    verified and has the same owner as the given domain.
    False otherwise.
    '''
    segments = domain.name.split('.')
    while segments:
        try:
            Domain.objects.get(name='.'.join(segments),
                               validated=True,
                               owner=domain.owner)
        except Domain.DoesNotExist:
            segments = segments[1:]
            continue
        return True
    return False


def validate_non_public_suffix(value):
    '''
    check that value is not a public suffix
    '''
    psl = PublicSuffixList()
    if psl.get_public_suffix(value) != psl.get_public_suffix('x.' + value):
        raise ValidationError(_('You cannot register public suffixes'))


def whois_validate_domain(value):
    '''
    Check that this is a domain according to whois
    '''
    try:
        whois.whois(value)
    except PywhoisError:
        msg = _('%(domain)s does not seem to be a valid domain name')
        raise ValidationError(msg % {'domain': value})
