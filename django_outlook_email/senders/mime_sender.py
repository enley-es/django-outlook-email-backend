import base64

import msal
import requests
from django.core.mail.message import sanitize_address
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from django_outlook_email.exceptions.microsoft_graph_exceptions import MicrosoftGraphException
from django_outlook_email.senders.base_sender import BaseSender


class MimeSender(BaseSender):
    def send(self, email_message):
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)

        message = email_message.message()

        try:
            response = requests.post(
                "https://outlook.office365.com/v1.0/users/" + from_email + "/sendMail",
                data=base64.b64encode(message.as_bytes(linesep="\r\n")),

                headers={"Authorization": "Bearer " + self.access_token, "Content-type": "text/plain"}
            )
        except requests.exceptions.RequestException:
            if not self.fail_silently:
                raise
            return False

        if response.status_code == 202:
            return True
        else:
            if not self.fail_silently:
                raise MicrosoftGraphException(response.status_code, response.content)
            return False