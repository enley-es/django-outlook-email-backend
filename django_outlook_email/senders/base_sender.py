class BaseSender:
    def __init__(self, access_token, fail_silently=False):
        self.access_token = access_token
        self.fail_silently = fail_silently
