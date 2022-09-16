from ..content_item_abc import ContentItemABC
from ... import description_item


class Image(ContentItemABC):
    def get_ssml(self):
        return []

    def get_description(self):
        return [
            description_item.Image(self._component.find("img"))
        ]

    @staticmethod
    def match_component(component):
        contents_without_nl = [content for content in component.contents if content != "\n"]
        return component.name == "div" and \
            len(contents_without_nl) > 0 and \
            contents_without_nl[0].name == "img"
