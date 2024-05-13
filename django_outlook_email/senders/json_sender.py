import base64
import mimetypes
from email.mime.base import MIMEBase

from django.conf import settings
from django_outlook_email.exceptions.microsoft_graph_exceptions import JsonSenderException
from django_outlook_email.senders.base_sender import BaseSender
from django.core.mail.message import sanitize_address
import requests

class JsonSender(BaseSender):

    def send(self, email_message):
        if not email_message.recipients():
            return False

        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [
            {"emailAddress": {"address": sanitize_address(addr, encoding)}} for addr in email_message.recipients()
        ]

        content, content_type = self._get_content_and_content_type(email_message)

        data = {
            "message": {
                "body": {
                    "content": content,
                    "contentType": "HTML"  # text/html #plain
                },
                "subject": email_message.subject,
                "toRecipients": recipients,
                "hasAttachments": False,
            }
        }

        attachments = self._get_attachments(email_message)
        if attachments:
            data["message"]["hasAttachments"] = True
            data["message"]["attachments"] = attachments
        print(data)
        response = requests.post(
            "https://graph.microsoft.com/v1.0/users/" + from_email + "/sendMail",
            json=data,

            headers={"Authorization": "Bearer " + self.access_token},
        )

        return True

    def _get_content_and_content_type(self, email_message):
        alternatives = self._get_alternatives(email_message)
        if alternatives:
            content = email_message.alternatives[0][0]
            content_type = email_message.alternatives[0][1]
        else:
            content = email_message.body
            content_type = email_message.content_subtype

        return content, content_type

    def _get_alternatives(self, email_message):
        html_alternatives = []
        text_plain_alternatives = []
        for alternative in email_message.alternatives:
            if alternative[1] == "text/plain":
                text_plain_alternatives.append(alternative[0])
            elif alternative[1] == "text/html":
                html_alternatives.append(alternative[0])
            else:
                raise JsonSenderException("Only text/plain and text/html alternatives are supported")

        if len(text_plain_alternatives) > 1:
            raise JsonSenderException("Only one text/plain alternative is supported")
        if len(html_alternatives) > 1:
            raise JsonSenderException("Only one text/html alternative is supported")

        return html_alternatives if html_alternatives else text_plain_alternatives

    def _get_attachments(self, email_message):
        attachments = []
        for attachment in email_message.attachments:
            if isinstance(attachment, MIMEBase):
                attachments.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": attachment.get_filename(),
                    "contentBytes":  attachment.get_payload(decode=True),
                    "contentType": attachment.get_content_type(),
                })
            else:
                attachments.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": attachment[0],
                    "contentBytes": base64.b64encode(attachment[1]).decode('utf-8'),
                    "contentType":  attachment[2],
                })
        return attachments

