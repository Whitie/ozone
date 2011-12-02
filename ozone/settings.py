# -*- coding: utf-8 -*-

import os

_PATH = os.path.dirname(os.path.abspath(__file__))

# Django settings for ozone project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Thorsten Weimann', 'weimann@bbz-chemie.de'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(_PATH, 'ozone.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL which holds the logo of the ozone page
LOGO_URL = '/static/img/logo.png'

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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'ozone.urls'

TEMPLATE_DIRS = (
    os.path.join(_PATH, 'base_templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'ozone.core',
    'ozone.orders',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'core.context_processors.userconf',
    'core.context_processors.set_global_vars',
)

AUTH_PROFILE_MODULE = 'core.UserProfile'

LOGIN_URL = '/core/login'
LOGOUT_URL = '/core/logout'

AUTHENTICATION_BACKENDS = (
    'ozone.core.ad_auth.ADAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Logging ######################################################################

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
        'ozone.ad_auth': {
            'handlers': ['console', 'file_access'],
            'level': 'DEBUG',
        },
    }
}
################################################################################

# Active Directory settings ####################################################

# FQDN or IP of the AD server
AD_DNS_NAME = '10.0.0.2'

# AD LDAP port
AD_LDAP_PORT = 389

# AD SSL (port should be 636 in order to use SSL)
AD_USE_SSL = False

# Path to cert file (only with AD_USE_SSL = True)
AD_CERT_FILE = ''

# Search dn for users and groups
AD_SEARCH_DN = 'ou=Nutzer,dc=bbzchemie,dc=de'

# NT4 domain name
AD_NT4_DOMAIN = 'BBZCHEMIE'

# Search fields in the AD
AD_SEARCH_FIELDS = ['mail', 'givenName', 'sn', 'sAMAccountName', 'memberOf']

# AD admin group (this users get admin status in django)
AD_MEMBERSHIP_ADMIN = ['EDV']

# AD groups that can access the app(s)
AD_MEMBERSHIP_REQ = AD_MEMBERSHIP_ADMIN + ['PVT']

# Create AD groups in django and assign users
AD_CREATE_GROUPS = True

################################################################################


# Make sure to use a path, which is writeable and not accesible over the web
SECRET_FILE = os.path.join(_PATH, '.secret')

# Don't change this (except os.urandom raises NotImplementedError)
try:
    with open(SECRET_FILE) as fp:
        SECRET_KEY = fp.read().strip()
except IOError:
    SECRET_KEY = os.urandom(40)
    with open(SECRET_FILE, 'w') as fp:
        fp.write(SECRET_KEY)
    try:
        os.chmod(SECRET_FILE, 0600)
    except:
        pass
