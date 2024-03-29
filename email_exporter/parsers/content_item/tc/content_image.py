from ..content_item_abc import ContentItemABC
from ... import description_item


class ContentImage(ContentItemABC):
    def get_ssml(self):
        return []

    def get_description(self):
        if (img := self._component.find("img")):
            yield description_item.Image(img)
        if (p := self._component.find("p")):
            yield description_item.Image(p)

    @staticmethod
    def match_component(component):
        if not hasattr(component, "contents"):
            return False
        contents_without_nl = [content for content in component.contents if content != "\n"]
        return component.name == "td" and \
            len(contents_without_nl) > 0 and \
            contents_without_nl[0].name == "img"
