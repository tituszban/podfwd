from ..content_item_abc import ContentItemABC


class Header(ContentItemABC):
    def __init__(self, component, content_item=None):
        super().__init__(component)
        assert content_item, "Header requires content_item parameter"
        self._content_item = content_item

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        return False
