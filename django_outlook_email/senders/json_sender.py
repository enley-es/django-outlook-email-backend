import base64
from email.mime.base import MIMEBase

from django.conf import settings
from django_outlook_email.exceptions.microsoft_graph_exceptions import JsonSenderException, MicrosoftGraphException
from django_outlook_email.senders.attachments.attachments_using_upload_session import UploadAttachment
from django_outlook_email.senders.base_sender import BaseSender
from django.core.mail.message import sanitize_address

from django_outlook_email.senders.content_types import MicrosoftContentType
from django_outlook_email.senders.microsoft_requests.microsoft_requests import MicrosoftRequests


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

        if not content:
            return False

        data = {
            "message": {
                "body": {
                    "content": content,
                    "contentType": content_type  # text/html #plain
                },
                "subject": email_message.subject,
                "toRecipients": recipients,
                "hasAttachments": False,
            }
        }

        return self._send_email(data, from_email, email_message)

    def _send_email(self, data, from_email, email_message):
        for attachment in email_message.attachments:

            # Check if the size of the attachment is greater than 3MB
            if len(attachment) > 3 * 1024 * 1024:
                return self._send_message_using_upload_session(data, from_email, email_message)
            else:
                pass

        return self._send_message_using_single_post(data, from_email, email_message)

    def _upload_attachment(self, attachment, message_id, from_email, file_name):
        upload_attachment = UploadAttachment(self.access_token, self.fail_silently, from_email)
        return upload_attachment.create(message_id, attachment, file_name)
    def _send_message_using_upload_session(self, data, from_email, email_message):
        microsoft_request = MicrosoftRequests(from_email, self.access_token, self.fail_silently)
        data["message"]["hasAttachments"] = True
        response = microsoft_request.post('messages', data.get("message"))
        if response:
            message_id = response.json()['id']
            for attachment in email_message.attachments:
                if isinstance(attachment, MIMEBase):
                    attachment = attachment
                    file_name = attachment.get_filename()
                else:
                    attachment = attachment[1]
                    file_name = attachment[0]
                    print(file_name)
                self._upload_attachment(attachment, message_id, from_email, file_name)
            microsoft_request = MicrosoftRequests(from_email, self.access_token, self.fail_silently)
            if microsoft_request.post(f'messages/{message_id}/send', data):
                return True
            else:
                return False
        return False


    def _send_message_using_single_post(self, data, from_email, email_message):
        attachments = self._get_attachments(email_message)
        if attachments:
            data["message"]["hasAttachments"] = True
            data["message"]["attachments"] = attachments

        microsoft_request = MicrosoftRequests(from_email, self.access_token, self.fail_silently)
        if microsoft_request.post('sendMail', data):
            return True
        else:
            return False



    def _get_content_and_content_type(self, email_message):
        alternatives = self._get_alternatives(email_message)
        if alternatives:
            content = email_message.alternatives[0][0]
            content_type = email_message.alternatives[0][1]
        else:
            content = email_message.body
            content_type = email_message.content_subtype

        return content, MicrosoftContentType.django_to_microsoft(content_type)

    def _get_alternatives(self, email_message):
        html_alternatives = []
        text_plain_alternatives = []
        for alternative in email_message.alternatives:
            if alternative[1] == "text/plain":
                text_plain_alternatives.append(alternative[0])
            elif alternative[1] == "text/html":
                html_alternatives.append(alternative[0])
            else:
                if self.fail_silently:
                    return []
                else:
                    raise JsonSenderException("Only text/plain and text/html alternatives are supported")

        if len(text_plain_alternatives) > 1 and not self.fail_silently:
            raise JsonSenderException("Only one text/plain alternative is supported")
        if len(html_alternatives) > 1 and not self.fail_silently:
            raise JsonSenderException("Only one text/html alternative is supported")

        return html_alternatives if html_alternatives else text_plain_alternatives

    def _get_attachments(self, email_message):
        attachments = []
        for attachment in email_message.attachments:
            if isinstance(attachment, MIMEBase):
                attachments.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": attachment.get_filename(),
                    "contentBytes":  base64.b64encode(attachment.get_payload(decode=True)).decode('utf-8'),
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

