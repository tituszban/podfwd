from abc import ABC

from email_exporter.inbox import InboxItem
from .parsed_item import ParsedItem


class ParserABC(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, content_item: InboxItem) -> ParsedItem:
        raise NotImplementedError()
