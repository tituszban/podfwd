from ..content_item_abc import ContentItemABC, ContentType


class NullContentItem(ContentItemABC):

    def get_ssml(self):
        return []

    def get_description(self):
        return []

    @property
    def content_type(self):
        return ContentType.null

    @staticmethod
    def match_component(component):
        return True
