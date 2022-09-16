from ..content_item_abc import ContentItemABC
from ssml import tags
from ... import description_item


class Paragraph(ContentItemABC):

    def get_ssml(self):
        return [
            tags.PText(self._get_text_content())
        ]

    def get_description(self):
        return [
            description_item.Text(self._component)
        ]

    @staticmethod
    def match_component(component):
        return component.name == "p"
