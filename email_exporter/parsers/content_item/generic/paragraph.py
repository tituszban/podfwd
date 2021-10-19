from ..content_item_abc import ContentItemABC
from ... import speech_item
from ... import description_item


class Paragraph(ContentItemABC):

    def get_ssml(self):
        return [
            speech_item.Paragraph(self._get_text_content())
        ]

    def get_description(self):
        return [
            description_item.Text(self._component)
        ]

    @staticmethod
    def match_component(component):
        return component.name == "p"
