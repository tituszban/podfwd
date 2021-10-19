from .description_item_abc import DescriptionItemABC
from .content_type import ContentType


class Embed(DescriptionItemABC):
    @property
    def content_type(self):
        return ContentType.embed
