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

# Django settings for peer project.

import datetime
import os

_ = lambda s: s

BASEDIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'no-reply@example.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'peer',                                      # Or path to database file if using sqlite3.
        'USER': 'peer',                                      # Not used with sqlite3.
        'PASSWORD': 'peer',                                  # Not used with sqlite3.
        'HOST': '',                                          # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                          # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASEDIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASEDIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, 'staticfiles'),
)

# Aditional theme custom styles
PEER_THEME = {
    'LINK_COLOR': '#5669CE',
    'LINK_HOVER': '#1631BC',
    'HEADING_COLOR': '#1631BC',
    'INDEX_HEADING_COLOR': '#ff7b33',
    'HEADER_BACKGROUND': '',
    'CONTENT_BACKGROUND': '',
    'FOOTER_BACKGROUND': '',
    'HOME_TITLE': 'Nice to meet you!!',
    'HOME_SUBTITLE': 'Say hello to federated worldwide services',
    'HOME_SLOGAN': 'Default text for the slogan',
    'JQUERY_UI_THEME': 'default-theme',
}

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'w^e-s0n)+#^ottb%lm+%9=_etmv8p&s3hacm6^i41+1+u_nw-3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)


# List of processors used by RequestContext to populate the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'peer.portal.context_processors.peer_theme',
    'peer.portal.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'peer.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'captcha',
    'registration',
    'djangosaml2',
    'peer.account',
    'peer.domain',
    'peer.entity',
    'peer.portal',
)

# needed for django-registration
ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'djangosaml2.backends.Saml2Backend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Email settings. Commented by security, but should be rewrite on a local or
# production settings
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 25

# reCaptcha keys. Not filled for security
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
# Uncomment the following line to make reCaptcha validation submits
# to be made over SSL
#RECAPTCHA_USE_SSL = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'peer.nagios': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# ENTITY METADATA VALIDATION
METADATA_VALIDATORS = (
    'peer.entity.validation.validate_xml_syntax',
    'peer.entity.validation.validate_domain_in_endpoints',
    'peer.entity.validation.validate_metadata_permissions',
    # 'peer.entity.validation.validate_domain_in_entityid',
    'peer.entity.validation.validate_schema',
)

# Permissions for metadata attribute. The metadata attribute is defined by
# its XPATH. The triplets are (<XPATH>, <Permission name>, <Permission
# description>)
#METADATA_PERMISSIONS = (
    #('/md:EntityDescriptor', 'entity_descriptor', 'Entity Descriptor'),
    #('.//md:ServiceDescription', 'service_descriptor', 'Service Description'),
    #('.//mdui:Description', 'description', 'Description'),
    #('.//md:OrganizationName', 'organization_name', 'Organization Name'),
#)

# VFF VERSIONED FILE BACKEND:
VFF_BACKEND = 'vff.git_backend.GitBackend'
# VFF (git backend) Path to the root of the git repo:
# VFF_REPO_ROOT = '/path/to/git/repo'
# VFF (git backend) Relative path within the git repo
# to the directory where vff keeps its managed files:
# VFF_REPO_PATH = 'my/dir'


# DOMAIN Verification by MAIL: Administrative email addresses supported
ADMINISTRATIVE_EMAIL_ADDRESSES = ('webmaster', 'hostmaster', 'abuse',
                                  'postmaster', 'admin')

# DOMAIN Invalidation: Send to the administrative contact of a domain
# returned by a WHOIS LOOKUP an email when the domain is validated to allow
# revoke the action
NOTIFY_DOMAIN_OWNER = False

# SAMLmetaJS plugins
SAML_META_JS_PLUGINS = ('info', 'org', 'contact', 'endpoints', 'certs',
                        'attributes', 'entityattrs', 'location')


# Terms of Use
USER_REGISTER_TERMS_OF_USE = os.path.join(BASEDIR,
                                          'user_register_terms_of_use.txt')
METADATA_IMPORT_TERMS_OF_USE = os.path.join(BASEDIR,
                                            'metadata_import_terms_of_use.txt')

# Max number of entries the global RSS feed will return
# MAX_FEED_ENTRIES = 10

# Expiration warnings
EXPIRATION_WARNING_TIMEDELTA = datetime.timedelta(days=1)

# Entities pagination
ENTITIES_PER_PAGE = 10

# Entities modificated nagios notification command (watch man send_nsca)
# Disabled if None
# NSCA_COMMAND = '/usr/sbin/send_nsca -H nagios.fqdn'
NSCA_COMMAND = None

# Nagios accept 0, 1, 2, 3 as 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
NSCA_NOTIFICATION_LEVEL = 3

# Nagios service name
NSCA_SERVICE = 'peer'

# Federated auth
SAML_ENABLED = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = SAML_ENABLED
SAML_CREATE_UNKNOWN_USER = True
SAML_ATTRIBUTE_MAPPING = {
    'mail': ('username', 'email'),
    'givenName': ('first_name', ),
    'sn': ('last_name', ),
}

SAML_ONE_IDP_SIGN_IN_BUTTON = _('Federated sign in')
SAML_SEVERAL_IDPS_SIGN_IN_BUTTON = _('Federated sign in')

SAML_CONFIG = {}  # YOU MUST OVERWRITE THIS IN THE LOCAL SETTINGS

# Remote user auth
REMOTE_USER_ENABLED = False


try:
    from local_settings import *
except ImportError:
    pass
