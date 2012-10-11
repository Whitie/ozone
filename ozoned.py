#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Run a Django project (or any other standard compliant WSGI application)
standalone with a CherryPy WSGI server."""

import os
import sys

import cherrypy

from argparse import ArgumentParser

from cherrypy.process import plugins


debug_env = {
    'engine.autoreload_on': True,
    'checker.on': True,
    'tools.log_headers_on': True,
    'request.show_tracebacks': True,
    'request.show_mismatched_params': True,
    'log.screen': True,
}


def import_object(import_path):
    """Call this function with a valid import path string. If you want the
    line: from mypackage.module import function
    executed, use: import_object('mypackage.module.function')
    and you get the function object back.
    """
    try:
        _path, objname = import_path.rsplit('.', 1)
    except ValueError:
        raise ValueError('Your path must contain at least one dot '
                         '(e.g. module.function).')
    module = __import__(_path, fromlist=[objname])
    obj = getattr(module, objname)
    return obj


def run(server_conf, args):
    cherrypy._cpconfig.environments['debug'] = debug_env
    cherrypy.config.update(server_conf)
    engine = cherrypy.engine
    # Setup all plugins
    if args.daemon and not args.debug:
        plugins.Daemonizer(engine).subscribe()
    if args.pidfile is not None:
        if args.pidfile[0] == '/':
            pidfile = args.pidfile
        else:
            pidfile = os.path.join('/var/run', args.pidfile)
        plugins.PIDFile(engine, pidfile).subscribe()
    if not args.no_drop_privileges:
        plugins.DropPrivileges(engine, 0664, args.user, args.group).subscribe()
    if hasattr(engine, 'signal_handler'):
        engine.signal_handler.subscribe()
    if hasattr(engine, 'console_control_handler'):
        engine.console_control_handler.subscribe()
    application = import_object(args.app_import_path)
    cherrypy.tree.graft(application)
    try:
        engine.start()
    except:
        sys.exit(1)
    else:
        engine.block()


def build_config(args):
    if args.debug:
        args.env = 'debug'
    c = {
        'environment': args.env,
        'server.socket_host': args.host,
        'server.socket_port': args.port,
        'server.thread_pool': args.threads,
        'log.access_file': os.path.join(args.logdir, 'access.log'),
        'log.error_file': os.path.join(args.logdir, 'error.log'),
    }
    c['log.screen'] = args.debug or args.log_to_screen
    if args.certfile and args.keyfile:
        c['server.ssl_module'] = 'builtin'
        c['server.ssl_certificate'] = args.certfile
        c['server.ssl_private_key'] = args.keyfile
    return c


def parse_commandline():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('app_import_path', help='Full import path of the '
        'application object to serve (e.g. myproject.wsgi.application)')
    parser.add_argument('-H', '--host', help='IP to bind server to [default: '
        '%(default)s]')
    parser.add_argument('-P', '--port', type=int, help='Port to listen on '
        '[default: %(default)s]')
    parser.add_argument('-t', '--threads', type=int, help='Number of worker '
        'threads to start [default: %(default)s]')
    parser.add_argument('-p', '--path', action='append', help='One or more '
        'paths to add to sys.path')
    parser.add_argument('-u', '--user', help='Unprivileged user to run the '
        'server [default: %(default)s]')
    parser.add_argument('-g', '--group', help='Group to run the server '
        '[default: %(default)s]')
    parser.add_argument('--no-drop-privileges', action='store_true',
        help='If this option is given, user and group are ignored. The '
        'server than run with the rights it is started [default: %(default)s]')
    parser.add_argument('--ssl-cert', dest='certfile', help='Path to SSL '
        'certificate file (if not given, no SSL is used)')
    parser.add_argument('--ssl-key', dest='keyfile', help='Path to SSL '
        'private key file')
    parser.add_argument('--log-to-screen', action='store_true',
        help='Write log output to screen (disabled in daemon mode) '
        '[default: %(default)s]')
    parser.add_argument('-l', '--logdir', help='Directory for access and '
        'error log (must exist and be writeable) [default: %(default)s]')
    parser.add_argument('--pidfile', help='Optional name of a pidfile, if '
        'it is only a name, it is appended to /var/run')
    parser.add_argument('-d', '--daemon', action='store_true',
        help='Run as daemon [default: %(default)s]')
    parser.add_argument('--env', choices=['staging', 'production',
        'embedded', 'test_suite', 'debug'], help='Choose CherryPy '
        'environment to use [default: %(default)s]')
    parser.add_argument('-D', '--debug', action='store_true',
        help='Start server with most output to screen [default: %(default)s]')
    parser.set_defaults(host='0.0.0.0', port=80, user='http', group='http',
        no_drop_privileges=False, log_to_screen=False, logdir='/var/log/djcpd',
        daemon=False, env='production', debug=False, threads=20)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_commandline()
    server_conf = build_config(args)
    if args.path is not None:
        for p in args.path:
            sys.path.insert(0, p)
    run(server_conf, args)
