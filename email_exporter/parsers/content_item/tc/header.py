from ..content_item_abc import ContentItemABC
from ... import speech_item


class Header(ContentItemABC):
    def __init__(self, component, to_item, inbox_item=None):
        super().__init__(component, to_item)
        assert inbox_item, "Header requires inbox_item parameter"
        self._inbox_item = inbox_item

    def get_ssml(self):
        title = self._inbox_item.title.replace("\r\n", "")
        author = self._get_text_content().replace("•", ";")
        return [
            speech_item.Paragraph(title),
            speech_item.Paragraph(author),
            speech_item.Pause("750ms")
        ]

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        return False
