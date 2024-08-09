import json

from django_outlook_email.exceptions.microsoft_graph_exceptions import MicrosoftGraphException
import requests

from django_outlook_email.senders.encoders.lazy_encoders import LazyEncoder
from requests.adapters import HTTPAdapter, Retry


class MicrosoftRequests:
    def __init__(self, from_email, access_token, fail_silently):
        self.from_email = from_email
        self.access_token = access_token
        self.fail_silently = fail_silently

    def post(self, endpoint, data):
        data = json.dumps(data, cls=LazyEncoder)
        try:

            session = requests.Session()
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[500])
            session.mount('https://', HTTPAdapter(max_retries=retries))

            response = session.post(
                "https://graph.microsoft.com/v1.0/users/" + self.from_email + "/" + endpoint,
                data=data,

                headers={"Authorization": "Bearer " + self.access_token, 'Content-Type': 'application/json'},
            )
        except requests.exceptions.RequestException:
            if not self.fail_silently:
                raise
            return False

        if response.status_code in [202, 201]:
            return response
        else:
            if not self.fail_silently:
                raise MicrosoftGraphException(response.status_code, response.content)
            return None


