# ANALYSEUR_DONNEES/analyse/utils.py

import requests
from django.conf import settings


def send_mailgun_email(subject, text, recipient_email):
    return requests.post(
        f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": f"Excited User <mailgun@{settings.MAILGUN_DOMAIN}>",
            "to": [recipient_email],
            "subject": subject,
            "text": text,
        },
    )
