from abc import ABC, abstractmethod
from typing import Generator
from email_exporter.inbox import InboxItem
from email_exporter.parsers.content_item import ContentItemABC


class ItemEmitter(ABC):
    @abstractmethod
    def get_items(self, inbox_item: InboxItem) -> Generator[ContentItemABC, None, None]:
        raise NotImplementedError()
