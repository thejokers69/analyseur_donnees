"""
WSGI config for analyseur_donnees project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyseur_donnees/wsgi.py
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analyseur_donnees.settings")

application = get_wsgi_application()
