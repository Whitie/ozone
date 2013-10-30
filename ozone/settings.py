# -*- coding: utf-8 -*-

import os
import sys

_PATH = os.path.dirname(os.path.abspath(__file__))
EXT_DIR = os.path.normpath(os.path.join(_PATH, '..', 'ext'))

sys.path.insert(0, EXT_DIR)

# Django settings for ozone project.

VERSION = '2.99.12'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Thorsten Weimann', 'weimann@bbz-chemie.de'),
)

MANAGERS = ADMINS

# Always set this in local_settings.py
DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Email settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
SERVER_EMAIL = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Dateformat to use (strftime notation)
DEFAULT_DATE_FORMAT = '%d.%m.%Y'
DEFAULT_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# Set to right directory in production
MEDIA_ROOT = os.path.join(_PATH, 'media')
STATIC_ROOT = os.path.join(_PATH, 'ozone_static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_DIRS = (
    os.path.join(_PATH, 'static'),
)

# URL which holds the logo of the ozone page
LOGO_URL = STATIC_URL + 'img/bbzlogo.png'

# Session configuration
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60
SESSION_COOKIE_NAME = 'ozone_sid'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
)

ROOT_URLCONF = 'ozone.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ozone.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(_PATH, 'base_templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'bootstrap_admin',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'active_directory',
    'core',
    'orders',
    'desktop',
    'south',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'core.context_processors.userconf',
    'core.context_processors.set_global_vars',
)

AUTH_PROFILE_MODULE = 'core.UserProfile'

LOGIN_URL = '/core/login'
LOGOUT_URL = '/core/logout'

AUTHENTICATION_BACKENDS = (
    'active_directory.auth.ADAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Default currency
CURRENCY = (u'Euro', u'€')

# Logging #####################################################################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(module)s %(message)s'
        },
        'verbose_req': {
            'format': '[%(asctime)s] %(levelname)s %(status_code)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_request': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose_req',
            'filename': os.path.join(_PATH, 'log', 'ozone_request.log'),
            'maxBytes': 1000 * 1024,
            'backupCount': 7,
        },
        'file_access': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(_PATH, 'log', 'ozone_access.log'),
            'maxBytes': 1000 * 1024,
            'backupCount': 7,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file_request'],
            'propagate': False,
            'level': 'INFO',
        },
        'active_directory': {
            'handlers': ['console', 'file_access'],
            'level': 'DEBUG',
        },
    }
}
###############################################################################

# Active Directory settings ###################################################

# FQDN or IP of the AD server
AD_DNS_NAME = '10.0.0.3'

# AD LDAP port
AD_LDAP_PORT = 389

# AD SSL (port should be 636 in order to use SSL)
AD_USE_SSL = False

# Path to cert file (only with AD_USE_SSL = True)
AD_CERT_FILE = ''

# Search dn for users
AD_SEARCH_DN = 'ou=SBSUsers,ou=Users,ou=MyBusiness,dc=bbz,dc=local'

# NT4 domain name
AD_NT4_DOMAIN = 'BBZ'

# Search fields in the AD
AD_SEARCH_FIELDS = ['mail', 'givenName', 'sn', 'sAMAccountName', 'memberOf']

# AD admin group (this users get admin status in django)
AD_MEMBERSHIP_ADMIN = ['EDV']

# AD groups that can access the app(s)
AD_MEMBERSHIP_REQ = AD_MEMBERSHIP_ADMIN + [
    'Pharmakanten',
    'Chemielaboranten',
    'QMB',
    'Leitung',
    'Verwaltung',
    'Biolaboranten',
    'Laborberufe',
    'Chemikanten',
    'QMTeam',
]

# Create AD groups in django and assign users
AD_CREATE_GROUPS = True

# Don't query AD again for x seconds (default: 8 hours)
# Set to 0 for no cache
AD_CACHE_TIME = 8 * 60 * 60
#AD_CACHE_TIME = 0

###############################################################################

# Latex settings ##############################################################
# Deprecated (moved to configuration model), will be removed in 3.1
LATEX = {
    'pdflatex': (r'P:/Portable/latex-portable/miktex-portable/miktex'
                 r'/bin/pdflatex.exe'),
    'options': ['-interaction=nonstopmode'],
    'build_dir': os.path.abspath(os.path.join(_PATH, '..', '_latex_build')),
    'fromfax': u'030 / 6 77 44 53',
    'fromphone': u'030 / 67 00 04-0',
    'fromname': u'Bildungswerk Nordostchemie e. V.',
    'fromaddress': u'Adlergestell 333, 12489 Berlin',
    'fromlogo': u'P:/container/bbz-tools/ozone/ozone/static/img/bbzlogo.png',
}

LATEX_BUILD_DIR = os.path.abspath(os.path.join(_PATH, '..', '_latex_build'))

###############################################################################

# Make sure to use a path, which is writeable and not accesible over the web
SECRET_FILE = os.path.join(_PATH, '.secret')

# Don't change this (except os.urandom raises NotImplementedError)
try:
    with open(SECRET_FILE) as fp:
        SECRET_KEY = fp.read().strip()
except IOError:
    # Hack for django 1.5 to ensure only ascii in SECRET_KEY
    from base64 import b64encode
    SECRET_KEY = b64encode(os.urandom(50))
    with open(SECRET_FILE, 'w') as fp:
        fp.write(SECRET_KEY)
    try:
        os.chmod(SECRET_FILE, 0600)
    except:
        pass

###############################################################################

# Global hacks
EXCLUDE_FROM_COMPANY_LIST = {'short_name': u'Alle'}

# Try to import local settings
try:
    from local_settings import *
except ImportError:
    print 'No local settings imported.'
