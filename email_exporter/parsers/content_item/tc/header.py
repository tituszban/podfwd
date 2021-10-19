from ..content_item_abc import ContentItemABC
from ... import speech_item
from ... import description_item


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
            description_item.Util(self._component.find("img")),
            description_item.Util(f"<p>{self._title}</p>"),
            description_item.Util(f"<p>{self._author}</p>")
        ]

    @staticmethod
    def match_component(component):
        return False
