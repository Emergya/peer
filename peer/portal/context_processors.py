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


DEFAULT_THEME = {
    'LINK_COLOR': '#5db39a',
    'LINK_HOVER': '',
    'HEADING_COLOR': '',
    'INDEX_HEADING_COLOR': '',
    'HEADER_BACKGROUND': '',
    'CONTENT_BACKGROUND': '',
    'FOOTER_BACKGROUND': '',
    'HOME_TITLE': 'Nice to meet you!!',
    'HOME_SUBTITLE': 'Say hello to federated worldwide services',
    'HOME_SLOGAN': 'A slogan that catches the purpose of the service',
    'JQUERY_UI_THEME': 'custom-theme',
}


def peer_theme(request):
    user_theme = getattr(settings, 'PEER_THEME', DEFAULT_THEME)
    theme = {}
    theme.update(DEFAULT_THEME)
    theme.update(user_theme)
    return theme


def auth(request):
    result = {
        'SAML_ENABLED': getattr(settings, 'SAML_ENABLED', False),
        'REMOTE_USER_ENABLED': getattr(settings, 'REMOTE_USER_ENABLED', False),
    }

    if result['SAML_ENABLED']:
        result.update({
            'SAML_ONE_IDP_SIGN_IN_BUTTON': getattr(settings, 'SAML_ONE_IDP_SIGN_IN_BUTTON', 'Federated sign in'),
            'SAML_SEVERAL_IDPS_SIGN_IN_BUTTON': getattr(settings, 'SAML_SEVERAL_IDPS_SIGN_IN_BUTTON', 'Federated sign in'),
        })

    return result
