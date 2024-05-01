import base64

import msal
import requests
from django.core.mail.message import sanitize_address
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from django_outlook_email.exceptions.microsoft_graph_exceptions import MicrosoftGraphException


class OutlookEmailBackend(BaseEmailBackend):

    access_token = None
    client_id = settings.OUTLOOK_CREDENTIALS["OUTLOOK_CLIENT_ID"]
    client_secret = settings.OUTLOOK_CREDENTIALS["OUTLOOK_CLIENT_SECRET"]
    tenant_id = settings.OUTLOOK_CREDENTIALS["OUTLOOK_TENANT_ID"]


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
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)

        message = email_message.message()

        try:
            response = requests.post(
                "https://graph.microsoft.com/v1.0/users/"+from_email+"/sendMail",
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


