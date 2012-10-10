#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Run Ozone standalone with CherryPy.
"""

import os
import sys

import cherrypy

from cherrypy.process import plugins


OZONED_PATH = os.path.abspath(os.path.dirname(__file__))


# Edit config here ############################################################

SERVER_IP = '10.0.0.196'
SERVER_PORT = 8005

USER = 'bbz'
GROUP = 'bbz'

LOG_PID_DIR = os.path.join(OZONED_PATH, 'ozone_run')
PID_FILE = os.path.join(LOG_PID_DIR, 'ozoned.pid')

SSL_CERT_FILE = '/etc/httpd/conf/server.crt'
SSL_KEY_FILE = '/etc/httpd/conf/server.key'

DJANGO_PROJECT_DIR = '/home/bbz/bbz-tools/ozone'

###############################################################################


config = {
    'global': {
        'environment': 'production',
        'server.socket_host': SERVER_IP,
        'server.socket_port': SERVER_PORT,
        'server.thread_pool': 20,
        # SSL
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': SSL_CERT_FILE,
        'server.ssl_private_key': SSL_KEY_FILE,
        # Logging
        'log.screen': False,
        'log.access_file': os.path.join(LOG_PID_DIR, 'access_ozoned.log'),
        'log.error_file': os.path.join(LOG_PID_DIR, 'error_ozoned.log'),
    }
}


def run():
    from ozone.wsgi import application
    cherrypy.config.update(config)
    engine = cherrypy.engine
    # Setup all plugins
    plugins.Daemonizer(engine).subscribe()
    plugins.PIDFile(engine, PID_FILE).subscribe()
    plugins.DropPrivileges(engine, 0644, USER, GROUP).subscribe()
    if hasattr(engine, 'signal_handler'):
        engine.signal_handler.subscribe()
    if hasattr(engine, 'console_control_handler'):
        engine.console_control_handler.subscribe()
    cherrypy.tree.graft(application)
    try:
        engine.start()
    except:
        sys.exit(1)
    else:
        engine.block()


if __name__ == '__main__':
    for p in (OZONED_PATH, DJANGO_PROJECT_DIR):
        if p not in sys.path:
            sys.path.insert(0, p)
    run()
