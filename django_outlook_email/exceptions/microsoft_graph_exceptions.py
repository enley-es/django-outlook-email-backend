class MicrosoftGraphException(Exception):
    """Microsoft graph error has ocurred."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__("status_code: {} ,message: {}".format(status_code, message))

class JsonSenderException(Exception):
    """Json Sender error has ocurred."""
    def __init__(self, status_code, message):
        self.message = message
        super().__init__(message)