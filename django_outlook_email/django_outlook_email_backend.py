import base64

import msal
import requests
from django.core.mail.message import sanitize_address
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from django_outlook_email.exceptions.microsoft_graph_exceptions import MicrosoftGraphException
from django_outlook_email.senders.json_sender import JsonSender
from django_outlook_email.senders.mime_sender import MimeSender


class OutlookEmailBackend(BaseEmailBackend):

    access_token = None
    client_id = settings.OUTLOOK_CREDENTIALS["OUTLOOK_CLIENT_ID"]
    client_secret = settings.OUTLOOK_CREDENTIALS["OUTLOOK_CLIENT_SECRET"]
    tenant_id = settings.OUTLOOK_CREDENTIALS["OUTLOOK_TENANT_ID"]
    send_format = settings.OUTLOOK_CREDENTIALS.get("OUTLOOK_SEND_FORMAT")


    def send_messages(self, email_messages):
        self._set_access_token()
        if not email_messages:
            return 0
        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        return num_sent


    def _set_access_token(self):
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority="https://login.microsoftonline.com/" + self.tenant_id,
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )

        self.access_token = result["access_token"]


    def _send(self, email_message):
        if self.send_format == "json":
            sender = JsonSender(self.access_token, self.fail_silently)
        else:
            sender = MimeSender(self.access_token, self.fail_silently)
        sender.send(email_message)

