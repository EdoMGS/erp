#!/usr/bin/env python
import os
import pathlib
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system.settings.dev')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    sys.path.append(str(pathlib.Path(__file__).resolve().parent))
    main()