from ..content_item_abc import ContentItemABC


class Image(ContentItemABC):
    def get_ssml(self):
        return []

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        contents_without_nl = [content for content in component.contents if content != "\n"]
        return component.name == "div" and \
            contents_without_nl[0].name == "img"
