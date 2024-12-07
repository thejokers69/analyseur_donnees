# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/utils.py

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


def send_mailgun_email(subject: str, text: str, recipient_email: str) -> bool:
    """
    Sends an email using the Mailgun API.

    :param subject: Subject of the email.
    :param text: Body of the email.
    :param recipient_email: Recipient's email address.
    :return: True if the email was sent successfully, False otherwise.
    :raises ImproperlyConfigured: If MAILGUN_DOMAIN or MAILGUN_API_KEY is not set.
    """
    mailgun_domain = getattr(settings, 'MAILGUN_DOMAIN', None)
    mailgun_api_key = getattr(settings, 'MAILGUN_API_KEY', None)

    if not mailgun_domain or not mailgun_api_key:
        raise ImproperlyConfigured("Mailgun settings MAILGUN_DOMAIN and MAILGUN_API_KEY must be set.")

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"Excited User <mailgun@{mailgun_domain}>",
                "to": [recipient_email],
                "subject": subject,
                "text": text,
            },
            timeout=10,  # seconds
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email via Mailgun: {e}")
        return False
