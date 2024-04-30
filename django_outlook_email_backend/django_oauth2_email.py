from django.core.mail.backends.smtp import EmailBackend
import msal
import requests
from django.core.mail.message import sanitize_address
from django.conf import settings





class OutlookOauth2EmailBackend(EmailBackend):

    access_token = None
    client_id = settings.OUTLOOK_CLIENT_ID
    client_secret = settings.OUTLOOK_CLIENT_SECRET

    def send_messages(self, email_messages):
        self._set_access_token()

        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
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
        recipients = [
            sanitize_address(addr, encoding) for addr in email_message.recipients()
        ]
        message = email_message.message()

        data = {
            "message": {
                "body": {
                    "content": message,
                    "contentType": "HTML"
                },
                "subject": "my subject",
                "toRecipients": [{
                    "emailAddress": {
                        "address": "mclaramunt@enley.com"
                    }
                }],
                "hasAttachments": False,
                "importance": "Normal"
            }
        }
        response = requests.post(
            "/users/"+from_email+"/sendMail",
            json=data,

            headers={"Authorization": "Bearer " + self.access_token},
        )

        return True


