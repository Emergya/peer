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

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'peer.domain.views',
    url(r'^add$', 'domain_add', name='domain_add'),
    url(r'^(?P<domain_id>\d+)(?:/token/(?P<token>\w+))?$', 'domain_verify',
        name='domain_verify'),
    url(r'^(?P<domain_id>\d+)/token/(?P<token>\w+)/invalidate$', 'domain_invalidate', name='domain_invalidate'),
    url(r'^(?P<domain_id>\d+)/remove$', 'domain_remove', name='domain_remove'),
    url(r'^(?P<domain_id>\d+)/force_ownership$', 'force_domain_ownership',
        name='force_domain_ownership'),
    url(r'^(?P<domain_id>\d+)/manage_team$', 'manage_domain_team',
        name='manage_domain_team'),
    url(r'^(?P<domain_id>\d+)/manage_domain$', 'manage_domain',
        name='manage_domain'),
    url(r'^(?P<domain_id>\d+)/list_delegates$', 'list_delegates',
        name='list_domain_delegates'),
    url(r'^(?P<domain_id>\d+)/add_delegate/(?P<username>.+)$',
        'add_delegate', name='add_domain_delegate'),
    url(r'^(?P<domain_id>\d+)/remove_delegate/(?P<username>.+)$',
        'remove_delegate', name='remove_domain_delegate'),
    url(r'^(?P<domain_id>\d+)/request-membership/(?P<username>.+)$',
        'request_membership', name='request_domain_team_membership'),
    url(r'^list-membership-requests$',
        'list_membership_requests', name='list_membership_requests'),
    url(r'^(?P<domain_id>\d+)/accept-membership/(?P<username>.+)$',
        'accept_membership_request', name='accept_membership_request'),
    url(r'^(?P<domain_id>\d+)/reject-membership/(?P<username>.+)$',
        'reject_membership_request', name='reject_membership_request'),
)
