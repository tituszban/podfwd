from ..content_item_abc import ContentItemABC
from ssml import tags
from ..util import get_text_content
from ... import description_item


class List(ContentItemABC):

    def get_ssml(self):
        return [
            tags.PText(get_text_content(component))
            for component in self._component.contents
            if component != "\n"
        ]

    def get_description(self):
        return [
            description_item.Text(self._component)
        ]

    @staticmethod
    def match_component(component):
        return component.name in ["ul", "ol"]
