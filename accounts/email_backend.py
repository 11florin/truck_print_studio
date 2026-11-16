"""Django email backend backed by Resend."""

import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.exceptions import ImproperlyConfigured


class ResendEmailBackend(BaseEmailBackend):
    """Send Django email messages through the Resend API."""

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        if not settings.RESEND_API_KEY:
            raise ImproperlyConfigured("RESEND_API_KEY must be configured.")

        resend.api_key = settings.RESEND_API_KEY
        sent_count = 0
        for message in email_messages:
            if not message.recipients():
                continue
            params = {
                "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
                "to": message.recipients(),
                "subject": message.subject,
                "text": message.body,
            }
            if message.content_subtype == "html":
                params["html"] = message.body
                params.pop("text")
            resend.Emails.send(params)
            sent_count += 1
        return sent_count
