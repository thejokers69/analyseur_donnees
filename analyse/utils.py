# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/utils.py

import os
import pandas as pd
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

# Load data 
def load_data(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension in [".xls", ".xlsx"]:
            return pd.read_excel(file_path, engine="openpyxl")
        elif file_extension == ".csv":
            return pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format.")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")

# Email addresses
def send_mailgun_email(subject: str, text: str, recipient_email: str) -> bool:
    """
    Envoie un email en utilisant l'API Mailgun.

    :param subject: Sujet de l'email.
    :param text: Corps de l'email.
    :param recipient_email: Adresse email du destinataire.
    :return: True si l'email a été envoyé avec succès, False sinon.
    :raises ImproperlyConfigured: Si MAILGUN_DOMAIN ou MAILGUN_API_KEY n'est pas défini.
    """
    mailgun_domain = getattr(settings, 'MAILGUN_DOMAIN', None)
    mailgun_api_key = getattr(settings, 'MAILGUN_API_KEY', None)

    if not mailgun_domain or not mailgun_api_key:
        raise ImproperlyConfigured("Les paramètres Mailgun MAILGUN_DOMAIN et MAILGUN_API_KEY doivent être définis.")

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"Excited User <{settings.DEFAULT_FROM_EMAIL}>",
                "to": [recipient_email],
                "subject": subject,
                "text": text,
            },
            timeout=10,  # secondes
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Échec de l'envoi de l'email via Mailgun : {e}")
        return False