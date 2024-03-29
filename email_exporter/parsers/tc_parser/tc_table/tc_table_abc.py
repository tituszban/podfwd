from abc import ABC, abstractmethod

from email_exporter.parsers.content_item import ContentItemABC


class TcTableABC(ABC):
    def __init__(self, component, content_item):
        self._component = component
        self._content_item = content_item

    @abstractmethod
    def get_items(self) -> list[ContentItemABC]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def match_component(component) -> bool:
        raise NotImplementedError

    @staticmethod
    def _has_n_child_of_type(_component, _type, n=1) -> bool:
        contents_without_nl = [content for content in _component.contents if content != "\n"]
        return len(contents_without_nl) == n and all(c.name == _type for c in contents_without_nl)
