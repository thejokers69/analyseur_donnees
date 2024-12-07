"""
ASGI config for analyseur_donnees project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyseur_donnees/asgi.py
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analyseur_donnees.settings")

application = get_asgi_application()
