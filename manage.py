# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:22:06 2025

@author: goranklasic
"""

#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_falcons.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()