from enum import Enum

class ContentType(Enum):
    TEXT_PLAIN = "plain"
    TEXT_HTML = "text/html"

class MicrosoftContentType(Enum):
    TEXT_PLAIN = "Text"
    TEXT_HTML = "HTML"

    @classmethod
    def django_to_microsoft(cls, content_type):
        content_type_mapping = {
            ContentType.TEXT_PLAIN.value: cls.TEXT_PLAIN.value,
            ContentType.TEXT_HTML.value: cls.TEXT_HTML.value,
        }
        try:
            return content_type_mapping[content_type]
        except KeyError:
            raise ValueError(f"Unsupported content type: {content_type}")