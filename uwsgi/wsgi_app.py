# /var/www/current/mysite/uwsgi/wsgi_app.py
#! /usr/bin/env python
import sys
import os
import django.core.handlers.wsgi
sys.path.append('/var/www/scratch2')
os.environ['DJANGO_SETTINGS_MODULE']='scratch.settings'
application = django.core.handlers.wsgi.WSGIHandler()