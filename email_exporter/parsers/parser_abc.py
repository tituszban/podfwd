from abc import ABC
from .content_item.content_item_abc import ContentItemABC
from .parsed_item import ParsedItem


class ParserABC(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, content_item: ContentItemABC) -> ParsedItem:
        raise NotImplementedError()
