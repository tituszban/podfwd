from ..content_item_abc import ContentItemABC, ContentType
from ... import speech_item


class Header(ContentItemABC):
    def __init__(self, component, to_item, inbox_item=None):
        super().__init__(component, to_item)
        assert inbox_item, "Header requires inbox_item parameter"
        self._inbox_item = inbox_item
        self._title = self._inbox_item.title.replace("\r\n", "")
        self._author = self._get_text_content().replace("•", ";")

    def get_ssml(self):
        
        return [
            speech_item.Paragraph(self._title),
            speech_item.Paragraph(self._author),
            speech_item.Pause("750ms")
        ]
    
    def get_description(self):
        return [
            self._component.find("img"),
            f"<p>{self._title}</p>",
            f"<p>{self._author}</p>"
        ]

    @property
    def content_type(self):
        return ContentType.util

    @staticmethod
    def match_component(component):
        return False
