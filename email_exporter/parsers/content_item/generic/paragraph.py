from ..content_item_abc import ContentItemABC, ContentType
from ... import speech_item


class Paragraph(ContentItemABC):

    def get_ssml(self):
        return [
            speech_item.Paragraph(self._get_text_content())
        ]

    def get_description(self):
        return super().get_description()

    @property
    def content_type(self):
        return ContentType.text

    @staticmethod
    def match_component(component):
        return component.name == "p"
