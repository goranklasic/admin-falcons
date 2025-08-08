# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:22:24 2025

@author: goranklasic
"""

# admin_falcons/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_falcons.settings')
application = get_wsgi_application()