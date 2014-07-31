# -*- coding: utf-8 -*-

import logging
import re

try:
    import ldap
except ImportError:
    ldap = None

from collections import defaultdict
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.utils.encoding import smart_str, smart_unicode
from django.utils import timezone

from active_directory.models import ADCache


logger = logging.getLogger('active_directory')


class ADAuthBackend:

    def __init__(self):
        if settings.AD_USE_SSL:
            logger.info('LDAP SSL enabled')
            prot = 'ldaps'
        else:
            prot = 'ldap'
        self.url = '{0}://{1}:{2}'.format(prot, settings.AD_DNS_NAME,
                                          settings.AD_LDAP_PORT)
        self.cache_time = settings.AD_CACHE_TIME
        logger.info('LDAP URL: %s', self.url)
        #logger.debug('Django PASSWORD_HASHERS: %r', settings.PASSWORD_HASHERS)
        logger.info('AD cache set to %d seconds', self.cache_time)

    def authenticate(self, username=None, password=None):
        if ldap is None:
            logger.warning('python-ldap cannot be imported')
            return
        # Windows usernames are case insensitive
        username = username.lower()
        logger.info('Trying to authenticate %s', username)
        if password is None or not len(password):
            logger.warning('Password for %s not provided', username)
            return
        if self.cache_time:
            logger.info('Checking cache...')
            user = self._check_cache(username, password)
            print user
            if user is not None:
                return user
        try:
            if settings.AD_USE_SSL:
                ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,
                                settings.AD_CERT_FILE)
            l = ldap.initialize(self.url)
            l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            binddn = u'{0}@{1}'.format(username, settings.AD_NT4_DOMAIN)
            l.simple_bind_s(smart_str(binddn), smart_str(password))
            l.unbind_s()
            return self._get_or_create_user(username, password)
        except ldap.INVALID_CREDENTIALS:
            logger.error('%s: Invalid credentials', username)
        except:
            logger.exception('Error in ADAuthBackend.authenticate')

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return

    def _check_cache(self, username, password):
        cache, created = ADCache.objects.get_or_create(username=username)
        now = timezone.now()
        expires = now + timedelta(seconds=self.cache_time)
        if created:
            logger.info('New user, creating cache entry')
            cache.expires = expires
            cache.save()
            return
        if cache.expires < now:
            logger.debug('Cache is expired, returning...')
            cache.expires = expires
            cache.save()
            return
        cache.expires = expires
        cache.save()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                logger.info('Found user, returning cached result')
                return user
        except:
            logger.exception('Error during cache lookup')

    def _get_or_create_user(self, username, password):
        logger.debug('_get_or_create_user(%r, ***) called', username)
        user_info = self._get_user_info(username, password)
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            created = False
        except User.DoesNotExist:
            user = User.objects.create_user(username=username,
                password=password)
            created = True
        user.save()
        if not created:
            logger.info('User %s found in database', username)
        else:
            if user_info is not None:
                logger.info('New user %s created', username)
            else:
                logger.error('No info for %s found in AD', username)
                return
        if user_info is None:
            user.is_active = False
            user.save()
            return user
        elif user_info['is_admin']:
            user.is_staff = True
            user.is_superuser = True
        user.first_name = user_info['first_name']
        user.last_name = user_info['last_name']
        user.email = user_info['mail']
        if settings.AD_CREATE_GROUPS:
            ad_groups = list(user.groups.filter(name__startswith=u'AD_'))
            user.groups.remove(*ad_groups)
            user.groups.add(*user_info['groups'])
        logger.info('Login: %s %s', user.first_name, user.last_name)
        user.save()
        return user

    def _check_groups(self, membership):
        logger.debug('Checking AD group membership')
        logger.debug('AD Strings: %r', ' / '.join(membership))
        is_valid = False
        is_admin = False
        groups = []
        pattern = re.compile(r'^CN=(?P<group_name>[\w|\d]+),')
        for group in membership:
            group_match = pattern.match(group)
            if group_match:
                g = group_match.group('group_name')
                logger.debug('Checking AD group %s', g)
                if g in settings.AD_MEMBERSHIP_REQ:
                    logger.debug('Group %s is valid', g)
                    is_valid = True
                    if settings.AD_CREATE_GROUPS:
                        name = u'AD_{0}'.format(smart_unicode(g)[:77])
                        dg, created = Group.objects.get_or_create(name=name)
                        if created:
                            logger.debug('Created group %s', dg.name)
                            dg.save()
                        groups.append(dg)
                    if g in settings.AD_MEMBERSHIP_ADMIN:
                        logger.debug('Group %s is admin group', g)
                        is_admin = True
        if not is_valid:
            logger.info('No needed AD group membership found')
        return is_admin, is_valid, groups

    def _get_user_info(self, username, password):
        try:
            user_info = defaultdict(unicode, username=username,
                                    password=password)
            if settings.AD_USE_SSL:
                ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,
                                settings.AD_CERT_FILE)
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            logger.debug('Initializing LDAP connection...')
            l = ldap.initialize(self.url)
            l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            binddn = u'{0}@{1}'.format(username, settings.AD_NT4_DOMAIN)
            logger.debug('LDAP bind: %s', binddn)
            l.bind_s(smart_str(binddn), smart_str(password))
            logger.debug('Searching...')
            result = l.search_ext_s(
                settings.AD_SEARCH_DN, ldap.SCOPE_SUBTREE,
                'sAMAccountName={0}'.format(smart_str(username)),
                settings.AD_SEARCH_FIELDS
            )[0][1]
            logger.debug('Result: %s', result)
            if 'memberOf' in result:
                membership = result['memberOf']
            else:
                logger.error('AD user %s has no group membership', username)
                return
            is_admin, is_valid, groups = self._check_groups(membership)
            if not is_valid:
                return
            user_info['is_admin'] = is_admin
            user_info['groups'] = groups
            if 'mail' in result:
                user_info['mail'] = smart_unicode(result['mail'][0])
            if 'sn' in result:
                user_info['last_name'] = smart_unicode(result['sn'][0])
            if 'givenName' in result:
                user_info['first_name'] = smart_unicode(result['givenName'][0])
            logger.debug('user_info: %r', user_info)
            l.unbind_s()
            return user_info
        except:
            logger.exception('Error while fetching user info from AD')
