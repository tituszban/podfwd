from ..content_item_abc import ContentItemABC
from ... import speech_item
from ..util import get_text_content


class List(ContentItemABC):

    def get_ssml(self):
        return [
            speech_item.Paragraph(get_text_content(component))
            for component in self._component.contents
            if component != "\n"
        ]

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        return component.name in ["ul", "ol"]
