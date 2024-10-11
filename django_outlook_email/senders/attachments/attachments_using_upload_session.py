import requests

from django_outlook_email.exceptions.microsoft_graph_exceptions import MicrosoftGraphException
from django_outlook_email.senders.microsoft_requests.microsoft_requests import MicrosoftRequests
from requests.adapters import HTTPAdapter, Retry



class UploadAttachment:
    CHUNK_SIZE = 2 * 1024 * 1024  # 4MB

    def __init__(self, access_token, fail_silently, from_email):
        self.access_token = access_token
        self.fail_silently = fail_silently
        self.from_email = from_email

    def create(self, message_id, attachment, file_name):
        microsoft_request = MicrosoftRequests(self.from_email, self.access_token, self.fail_silently)
        data = {
            "AttachmentItem": {
                "attachmentType": "file",
                "name": str(file_name),
                "size": len(attachment)
            }
        }

        response = microsoft_request.post(f'messages/{message_id}/attachments/createUploadSession', data)
        return self._upload_attachment(response.json()['uploadUrl'], attachment)

    def _upload_attachment(self, upload_url, attachment):
        chunk_number = 0
        response = None
        while True:
            chunk = attachment[chunk_number * self.CHUNK_SIZE: (chunk_number + 1) * self.CHUNK_SIZE]
            if not chunk:
                break

            # Calculate the range of bytes for the chunk
            start_range = chunk_number * self.CHUNK_SIZE
            end_range = start_range + len(chunk) - 1
            file_size = len(attachment)

            # Prepare the headers
            headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Length': str(len(chunk)),
                'Content-Range': f'bytes {start_range}-{end_range}/{file_size}',
            }
            print(headers)
            print(f'Uploading chunk {chunk_number + 1} of {file_size / self.CHUNK_SIZE}')

            try:
                session = requests.Session()
                retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],)
                session.mount('https://', HTTPAdapter(max_retries=retries))

                response = session.put(
                    upload_url,
                    headers = headers,
                    data = chunk
                )
            except requests.exceptions.RequestException:
                if not self.fail_silently:
                    raise
                return False

            if response.status_code not in [200,201,202]:
                if not self.fail_silently:
                    raise MicrosoftGraphException(response.status_code, response.content)
                break
            chunk_number += 1

        if response and response.status_code == 200:
            location_header = response.headers.get('Location')
            if location_header:
                attachment_id = location_header.split('/')[-1]
                print(f"Attachment ID: {attachment_id}")
                return attachment_id

        return None
