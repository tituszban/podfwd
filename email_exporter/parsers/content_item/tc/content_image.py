from email_exporter.parsers.content_item.substack.tweet import Image
from ..content_item_abc import ContentItemABC
from ... import description_item


class ContentImage(ContentItemABC):
    def get_ssml(self):
        return []

    def get_description(self):
        return [
            description_item.Image(self._component.find("img")),
            description_item.Image(self._component.find("p"))
        ]

    @staticmethod
    def match_component(component):
        contents_without_nl = [content for content in component.contents if content != "\n"]
        return component.name == "td" and \
            contents_without_nl[0].name == "img"
