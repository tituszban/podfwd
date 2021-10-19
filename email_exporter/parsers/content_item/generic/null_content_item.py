from ..content_item_abc import ContentItemABC


class NullContentItem(ContentItemABC):

    def get_ssml(self):
        return []

    def get_description(self):
        return []

    @staticmethod
    def match_component(component):
        return True
