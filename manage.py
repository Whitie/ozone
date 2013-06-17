#!/usr/bin/env python2

import os
import sys

# For testing
_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_PATH, '..', 'ozone_extensions'))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ozone.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
