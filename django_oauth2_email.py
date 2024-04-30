from django.core.mail.backends.smtp import EmailBackend

class OutlookOauth2EmailBackend(EmailBackend):
    def send_messages(self, email_messages):
        pass
